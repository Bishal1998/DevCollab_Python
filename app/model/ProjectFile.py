from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Project, User


class ProjectFile(SQLModel, table=True):
    __tablename__ = "project_files"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    project_id: UUID = Field(foreign_key="projects.id")
    project: Project = Relationship(
        back_populates="project_file", sa_relationship_kwargs={"lazy": "selectin"}
    )

    path: str = Field(unique=True, nullable=False)

    minio_object_key: str

    created_by_id: UUID = Field(foreign_key="users.id")
    created_by: User = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ProjectFile.created_by_id]",
            "lazy": "selectin",
        }
    )
    updated_by_id: Optional[UUID] = Field(
        foreign_key="users.id", default=None, nullable=True
    )
    updated_by: Optional[User] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ProjectFile.updated_by_id]",
            "lazy": "selectin",
        }
    )

    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )

    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            postgresql.TIMESTAMP, default=None, nullable=True, onupdate=datetime.now
        )
    )
