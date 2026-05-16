from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReadTodayUsage(BaseModel):
    id: UUID
    tokens_used: int
    tokens_limit: int
    previews_running: int
    previews_limit: int
    created_at: datetime
