import asyncio
import json
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.ai.clients import AiClient
from app.ai.parser import parse_response
from app.ai.prompts import build_system_prompt
from app.model import ChatMessage, ChatSession
from app.model.chat_message import MessageRole
from app.schema import ChatEvent, ChatEventType
from app.services.storage_service import StorageService


class AiService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_client = AiClient()
        self.storage = StorageService()

    async def chat(
        self,
        project_id: UUID,
        prompt: str,
        user_id: UUID,
        session_id: UUID | None = None,
    ) -> AsyncGenerator[ChatEvent, None]:

        # --- Session management ---
        if session_id:
            chat_session = await self._get_session(session_id)
        else:
            chat_session = await self._create_session(project_id, user_id)

        # Tell the frontend the session ID so it can continue the conversation
        yield ChatEvent(
            ChatEventType.SESSION_CREATED,
            {"session_id": str(chat_session.id)},
        )

        messages = await self._build_message_history(chat_session.id)
        messages.append({"role": "user", "content": prompt})

        await self._save_message(chat_session.id, MessageRole.USER, prompt)

        file_tree = await self._get_file_tree(project_id)
        system_prompt = build_system_prompt(file_tree)

        async def tool_executor(name: str, args: dict) -> str:
            return await self._execute_tool(name, args, project_id)

        # --- Stream LLM response, forwarding all ChatEvents ---
        full_response = ""

        async for event in self.ai_client.stream_with_tools(
            system_prompt=system_prompt,
            messages=messages,
            tool_executor=tool_executor,
        ):
            # Accumulate text for parsing later
            if event.event_type == ChatEventType.TEXT_CHUNK:
                full_response += event.data.get("content", "")

            # Forward every event to the router
            yield event

        # --- Parse and persist ---
        parsed = parse_response(full_response)

        assistant_content = (
            "\n\n".join(msg.content for msg in parsed.messages) or full_response
        )

        await self._save_message(
            chat_session.id, MessageRole.ASSISTANT, assistant_content
        )

        # Save files and emit file_saved events
        for file in parsed.files:
            await self._save_file(project_id, file.path, file.content)
            yield ChatEvent(
                ChatEventType.FILE_SAVED,
                {"path": file.path},
            )

        # Signal completion
        yield ChatEvent(
            ChatEventType.DONE,
            {"session_id": str(chat_session.id)},
        )

    async def _execute_tool(self, name: str, args: dict, project_id: UUID) -> str:
        if name == "get_file_content":
            paths = args.get("paths", [])
            contents = {}
            for path in paths:
                content = await self._read_file(project_id, path)
                contents[path] = content
            return json.dumps(contents, indent=2)
        return json.dumps({"error": f"Unknown tool: {name}"})

    async def _get_session(self, session_id: UUID) -> ChatSession:
        chat_session = await self.session.get(ChatSession, session_id)
        if not chat_session:
            raise ValueError(f"Chat session {session_id} not found")
        return chat_session

    async def _create_session(self, project_id: UUID, user_id: UUID) -> ChatSession:
        chat_session = ChatSession(project_id=project_id, user_id=user_id)
        self.session.add(chat_session)
        await self.session.commit()
        await self.session.refresh(chat_session)
        return chat_session

    async def _build_message_history(self, session_id: UUID) -> list[dict]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(col(ChatMessage.created_at).asc())
        )
        db_messages = result.scalars().all()
        return [{"role": msg.role, "content": msg.content} for msg in db_messages]

    async def _save_message(
        self,
        session_id: UUID,
        role: MessageRole,
        content: str,
        tool_calls: str | None = None,
        tool_call_id: str | None = None,
        tokens_used: int | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            tokens_used=tokens_used,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def _get_file_tree(self, project_id: UUID) -> str:
        return await asyncio.to_thread(self.storage.get_file_tree, str(project_id))

    async def _read_file(self, project_id: UUID, path: str) -> str:
        return await asyncio.to_thread(self.storage.read_file, str(project_id), path)

    async def _save_file(self, project_id: UUID, path: str, content: str) -> None:
        await asyncio.to_thread(self.storage.write_file, str(project_id), path, content)
