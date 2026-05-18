from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReadTodayUsage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tokens_used: int
    tokens_limit: int
    previews_running: int
    previews_limit: int
    created_at: datetime
