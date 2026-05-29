import json
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.ai.clients import AiClient
from app.ai.parser import parse_response
from app.ai.prompts import build_system_prompt
from app.model import ChatMessage, ChatSession
from app.model.chat_message import MessageRole


class AIService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.client = AiClient()

    async def chat(
        self,
        project_id: UUID,
        prompt: str,
        user_id: UUID,
        session_id: UUID | None = None,
    ) -> AsyncGenerator[str, None]:

        # get existing session or create a new one

        if session_id:
            chat_session = await self._get_session(session_id)
        else:
            chat_session = await self._create_session(project_id, user_id)

        ## build conversation history

        messages = await self._build_message_history(chat_session.id)

        messages.append({"role": "user", "content": prompt})

        await self._save_message(chat_session.id, MessageRole.USER, prompt)

        file_tree = await self._get_file_tree(project_id)

        system_prompt = build_system_prompt(file_tree)

        full_response = ""

        async for chunk in self.ai_client.stream_with_tools(
            system_prompt=system_prompt,
            messages=messages,
            tool_executor=self._execute_tool,
        ):
            full_response += chunk
            yield chunk

        parsed = parse_response(full_response)

        assistant_content = (
            "\n\n".join(msg.content for msg in parsed.messages) or full_response
        )
        await self._save_message(
            chat_session.id, MessageRole.ASSISTANT, assistant_content
        )

        for file in parsed.files:
            await self._save_file(project_id, file.path, file.content)

    async def _execute_tool(self, name: str, args: dict) -> str:
        if name == "get_file_content":
            paths = args.get("paths", [])
            contents = {}
            for path in paths:
                content = await self._read_file(path)
                contents[path] = content

        return json.dumps({"error": f"Unknown tool: {name}"})

    async def _get_session(self, session_id: UUID) -> ChatSession:
        chat_session = await self.session.get(ChatSession, session_id)

        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session {chat_session} not found.",
            )

        return chat_session

    async def _create_session(self, project_id: UUID, user_id: UUID) -> ChatSession:
        chat_session = ChatSession(user_id=user_id, project_id=project_id)

        self.session.add(chat_session)
        await self.session.commit()
        await self.session.refresh(chat_session)

        return chat_session

    async def _build_message_history(self, session_id: UUID) -> list[dict]:
        result = await self.session.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(col(ChatMessage.created_at).asc())
        )
        db_messages = result.all()

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
        """
        Get the project's file tree from MinIO.
        TODO: Implement with MinIO client — list all objects
        under the project's prefix and format as a tree string.
        """
        return "(empty project — MinIO not connected yet)"

    async def _read_file(self, path: str) -> str:
        """
        Read a single file's content from MinIO.
        TODO: Implement with MinIO client — get_object().
        """
        return f"(file not found: {path} — MinIO not connected yet)"

    async def _save_file(self, project_id: UUID, path: str, content: str) -> None:
        """
        Write a file to MinIO under the project's prefix.
        TODO: Implement with MinIO client — put_object().
        """
        pass
