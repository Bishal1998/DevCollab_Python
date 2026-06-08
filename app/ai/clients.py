import json
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI

from app.schema import ChatEvent, ChatEventType
from config import ai_settings

from .tools import TOOLS


class AiClient:
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
    ) -> AsyncGenerator[ChatEvent, None]:
        """
        Now yields ChatEvent objects instead of raw strings.
        The service/router converts these to SSE format.
        """
        rounds = 0

        while rounds < ai_settings.AI_TOOL_MAX_ROUNDS:
            rounds += 1

            collected_text = ""
            tool_calls_accumulator: dict[int, dict] = {}

            try:
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
            except Exception as e:
                print(f"[AiClient] API call failed: {type(e).__name__}: {e}")
                yield ChatEvent(ChatEventType.ERROR, {"message": str(e)})
                return

            try:
                async for chunk in stream:
                    choice = chunk.choices[0] if chunk.choices else None
                    if not choice:
                        continue

                    delta = choice.delta

                    if delta.content:
                        collected_text += delta.content
                        yield ChatEvent(
                            ChatEventType.TEXT_CHUNK,
                            {"content": delta.content},
                        )

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

                    if choice.finish_reason == "stop":
                        return

                    if choice.finish_reason == "tool_calls":
                        break

            except Exception as e:
                print(f"[AiClient] Stream error: {type(e).__name__}: {e}")
                yield ChatEvent(ChatEventType.ERROR, {"message": str(e)})
                return

            if not tool_calls_accumulator:
                return

            # --- Build assistant message for conversation history ---
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

            assistant_msg = {"role": "assistant", "tool_calls": assistant_tool_calls}
            if collected_text:
                assistant_msg["content"] = collected_text
            messages.append(assistant_msg)

            # --- Execute tools with lifecycle events ---
            for tc in tool_calls_accumulator.values():
                try:
                    args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    args = {}

                # Emit tool_call_start so frontend can show a spinner
                yield ChatEvent(
                    ChatEventType.TOOL_CALL_START,
                    {"tool": tc["name"], **args},
                )

                result = await tool_executor(tc["name"], args)

                # Emit tool_call_end so frontend can hide the spinner
                yield ChatEvent(
                    ChatEventType.TOOL_CALL_END,
                    {"tool": tc["name"]},
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    }
                )

            print(
                f"[AiClient] Tool round {rounds} complete. Tools called: {[tc['name'] for tc in tool_calls_accumulator.values()]}"
            )
