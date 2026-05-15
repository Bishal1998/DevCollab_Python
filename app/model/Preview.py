from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Project


class PreviewStatus(str, Enum):
    CREATING = "creating"
    RUNNING = "running"
    FAILED = "failed"
    TERMINATED = "terminated"


class Preview(SQLModel, table=True):
    __tablename__ = "previews"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    project_id: UUID = Field(foreign_key="projects.id", unique=True)
    project: Project = Relationship(
        back_populates="preview", sa_relationship_kwargs={"lazy": "selectin"}
    )

    namespace: str
    pod_name: str
    preview_url: str
    status: PreviewStatus = Field(default=PreviewStatus.CREATING, nullable=False)

    started_at: Optional[datetime] = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=None, nullable=True)
    )
    terminated_at: Optional[datetime] = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=None, nullable=True)
    )
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )
