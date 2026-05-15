from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Project, User


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    project_id: UUID = Field(foreign_key="projects.id", nullable=False)

    user: User = Relationship(
        back_populates="chat_message", sa_relationship_kwargs={"lazy": "selectin"}
    )

    project: Project = Relationship(
        back_populates="chat_message", sa_relationship_kwargs={"lazy": "selectin"}
    )

    role: MessageRole = Field(default=MessageRole.USER, nullable=False)
    content: str
    tool_calls: str
    tool_call_id: str
    tokens_used: str
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
