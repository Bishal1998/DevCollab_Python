from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Project, User


class ProjectMemberRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    ADMIN = "admin"


class ProjectMember(SQLModel, table=True):
    __tablename__ = "project_members"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", primary_key=True)

    user: User = Relationship(back_populates="project_member")
    project: Project = Relationship(back_populates="project_member")

    role: ProjectMemberRole = Field(default=ProjectMemberRole.VIEWER, nullable=False)

    invited_by_id: Optional[UUID] = Field(
        default=None, foreign_key="users.id", nullable=True
    )
    invited_by: Optional[User] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ProjectMember.invited_by_id]",
            "lazy": "selectin"
        }
    )

    invited_at: Optional[datetime] = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=None, nullable=True)
    )
