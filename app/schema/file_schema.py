from datetime import datetime

from pydantic import BaseModel


class BaseFile(BaseModel):
    path: str


class ReadFile(BaseFile):
    created_at: datetime
    size: int
    type: str
