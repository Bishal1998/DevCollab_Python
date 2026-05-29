import json
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI

from ai.tools import TOOLS
from config import ai_settings


class AiClient:
    """
    Wraps the OpenAI-compatible async client (pointed at OpenRouter).
    Handles streaming responses and the tool-use orchestration loop.
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=ai_settings.OPEN_ROUTER_API_KEY,
        )
        self.model = ai_settings.AI_MODEL
        self.max_tokens = ai_settings.AI_MAX_TOKENS

    async def stream_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        tool_executor: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from the LLM, handling tool calls automatically.

        The tool-use loop:
        1. Send messages to LLM with streaming
        2. If LLM returns tool_calls → execute them → append results → re-send
        3. Repeat until LLM produces a final text response (no more tool calls)

        Yields text chunks as they arrive for real-time SSE forwarding.
        """
        rounds = 0

        while rounds < ai_settings.AI_TOOL_MAX_ROUNDS:
            rounds += 1

            # --- Stream the response ---
            # We need to both yield text chunks AND accumulate tool calls.
            # Text chunks go to the frontend immediately.
            # Tool calls are collected and executed after the stream ends.

            collected_text = ""
            tool_calls_accumulator: dict[int, dict] = {}
            # ^ Tool call chunks arrive in pieces across multiple stream events.
            #   We accumulate them by index, then assemble complete calls at the end.

            stream = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages,
                ],
                tools=TOOLS,
                stream=True,
            )

            async for chunk in stream:
                choice = chunk.choices[0] if chunk.choices else None
                if not choice:
                    continue

                delta = choice.delta

                # --- Text content: yield immediately ---
                if delta.content:
                    collected_text += delta.content
                    yield delta.content

                # --- Tool call chunks: accumulate ---
                # OpenAI streams tool calls in pieces:
                #   First chunk has: index, id, function.name
                #   Subsequent chunks have: index, function.arguments (partial JSON)
                # We collect all pieces, then assemble when the stream ends.
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_accumulator:
                            tool_calls_accumulator[idx] = {
                                "id": "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc.id:
                            tool_calls_accumulator[idx]["id"] = tc.id
                        if tc.function and tc.function.name:
                            tool_calls_accumulator[idx]["name"] = tc.function.name
                        if tc.function and tc.function.arguments:
                            tool_calls_accumulator[idx]["arguments"] += (
                                tc.function.arguments
                            )

                # --- Check if stream is done ---
                if choice.finish_reason == "stop":
                    # Model finished with text, no tool calls. We're done.
                    return

                if choice.finish_reason == "tool_calls":
                    # Model wants to call tools. Break out to execute them.
                    break

            # --- No tool calls accumulated? We're done ---
            if not tool_calls_accumulator:
                return

            # --- Execute tool calls ---
            # 1. Build the assistant message with tool calls (for conversation history)
            # 2. Execute each tool
            # 3. Append tool results as separate messages
            # 4. Loop back to send updated conversation to LLM

            assistant_tool_calls = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                }
                for tc in tool_calls_accumulator.values()
            ]

            # Add assistant's response (with tool calls) to conversation
            assistant_msg = {"role": "assistant", "tool_calls": assistant_tool_calls}
            if collected_text:
                assistant_msg["content"] = collected_text
            messages.append(assistant_msg)

            # Execute each tool and add results
            for tc in tool_calls_accumulator.values():
                try:
                    args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    args = {}

                result = await tool_executor(tc["name"], args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    }
                )

            # Loop continues — next iteration sends the updated
            # conversation (with tool results) back to the LLM
