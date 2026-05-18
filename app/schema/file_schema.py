from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseFile(BaseModel):
    path: str


class ReadFile(BaseFile):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    size: int
    type: str
