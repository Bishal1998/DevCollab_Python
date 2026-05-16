from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import (
        ChatMessage,
        ChatSession,
        ProjectMember,
        Subscription,
        UsageLog,
    )


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, default=uuid4))
    email: EmailStr = Field(
        sa_column=Column(postgresql.VARCHAR, unique=True, nullable=False)
    )
    hashed_password: str = Field(nullable=False)
    name: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            postgresql.TIMESTAMP, default=None, onupdate=datetime.now, nullable=True
        )
    )
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=None, nullable=True)
    )

    subscription: Optional["Subscription"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    project_member: List["ProjectMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "[ProjectMember.user_id]",
            "lazy": "selectin",
        },
    )
    chat_session: List["ChatSession"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    chat_message: List["ChatMessage"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    usage_log: List["UsageLog"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
