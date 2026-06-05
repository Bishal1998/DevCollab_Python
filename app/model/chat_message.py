from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import ChatSession


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    role: MessageRole = Field(default=MessageRole.USER, nullable=False)
    content: str
    tool_calls: Optional[str] = Field(
        sa_column=Column(postgresql.TEXT, default=None, nullable=True)
    )
    tool_call_id: Optional[str] = Field(
        sa_column=Column(postgresql.VARCHAR, default=None, nullable=True)
    )
    tokens_used: Optional[int] = Field(
        sa_column=Column(postgresql.INTEGER, default=None, nullable=True)
    )

    session_id: UUID = Field(foreign_key="chat_sessions.id", nullable=False)
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )

    chat_session: Optional["ChatSession"] = Relationship(
        back_populates="chat_messages", sa_relationship_kwargs={"lazy": "selectin"}
    )
