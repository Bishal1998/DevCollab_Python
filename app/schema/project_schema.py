from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schema.project_member_schema import ReadProjectMember


class BaseProject(BaseModel):
    name: str = Field(min_length=3)


class CreateProject(BaseProject):
    pass


class ReadProject(BaseProject):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    project_member: List[ReadProjectMember] = []


class UpdateProject(BaseModel):
    name: str | None = Field(default=None)
    is_public: bool | None = Field(default=None)
