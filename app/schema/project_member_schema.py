from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.model.project_member import ProjectMemberRole


class ReadProjectMember(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    role: ProjectMemberRole
    invited_by_id: Optional[UUID] = None
    invited_at: Optional[datetime] = None


class InviteMember(BaseModel):
    email: EmailStr
    role: ProjectMemberRole
