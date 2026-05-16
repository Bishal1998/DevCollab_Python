from uuid import UUID

from pydantic import BaseModel


class ReadPlan(BaseModel):
    id: UUID
    name: str
    max_projects: int
    max_tokens_per_day: int
    max_previews: int
    unlimited_ai: bool
    active: bool
