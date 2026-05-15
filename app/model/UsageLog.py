from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Project, User


class UsageLog(SQLModel, table=True):
    __tablename__ = "usuage_logs"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    project_id: UUID = Field(foreign_key="projects.id", nullable=False)

    user: User = Relationship(
        back_populates="usuage_log", sa_relationship_kwargs={"lazy": "selectin"}
    )

    project: Project = Relationship(
        back_populates="usage_log", sa_relationship_kwargs={"lazy": "selectin"}
    )

    action: str
    tokens_used: int
    duration_ms: int
    metadata: str
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )
