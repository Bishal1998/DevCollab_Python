from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BaseProject(BaseModel):
    name: str = Field(min_length=3)


class CreateProject(BaseProject):
    pass


class ReadProject(BaseProject):
    id: UUID
    name: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] | None = Field(default=None)
    deleted_at: Optional[datetime] | None = Field(default=None)


class UpdateProject(BaseModel):
    name: str | None = Field(default=None)
    is_public: bool | None = Field(default=None)
