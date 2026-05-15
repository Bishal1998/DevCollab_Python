from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import ProjectFile, ProjectMember


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    name: str = Field(nullable=False)

    is_public: bool = Field(default=False)
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

    project_member: list[ProjectMember] = Relationship(
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )

    project_file: list[ProjectFile] = Relationship(
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )
