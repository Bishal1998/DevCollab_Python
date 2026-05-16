from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Project, User


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    project_id: UUID = Field(foreign_key="projects.id", nullable=False)
    title: str = Field(nullable=False)
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

    user: Optional["User"] = Relationship(
        back_populates="chat_session", sa_relationship_kwargs={"lazy": "selectin"}
    )
    project: Optional["Project"] = Relationship(
        back_populates="chat_session", sa_relationship_kwargs={"lazy": "selectin"}
    )
