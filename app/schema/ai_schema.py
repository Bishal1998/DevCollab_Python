from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    project_id: UUID
    prompt: str = Field(min_length=1, max_length=10000)
    session_id: UUID | None = Field(default=None)
