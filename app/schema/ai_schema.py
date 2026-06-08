import json
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    project_id: UUID
    prompt: str = Field(min_length=1, max_length=10000)
    session_id: UUID | None = Field(default=None)


class ChatEventType(str, Enum):
    SESSION_CREATED = "session_created"
    TEXT_CHUNK = "text_chunk"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    FILE_SAVED = "file_saved"
    DONE = "done"
    ERROR = "error"


class ChatEvent:
    def __init__(self, event_type: ChatEventType, data: dict | None = None):
        self.event_type = event_type
        self.data = data or {}

    def to_sse(self) -> str:
        json_data = json.dumps(self.data)
        return f"event: {self.event_type.value}\ndata: {json_data}\n\n"
