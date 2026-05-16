import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BaseProject(BaseModel):
    name: str = Field(min_length=3)


class CreateProject(BaseProject):
    pass


class ReadProject(BaseProject):
    id: UUID
    name: str
    is_public: False
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime


class UpdateProject(BaseProject):
    name: str | None = Field(default=None)
    is_public: bool | None = Field(default=None)
