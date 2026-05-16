from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.model.project_member import ProjectMemberRole


class ReadProjectMember(BaseModel):
    name: str
    email: EmailStr
    user_id: UUID
    project_id: UUID
    role: ProjectMemberRole
    invited_by_id: UUID
    invited_at: datetime


class InviteMember(BaseModel):
    email: EmailStr
    role: ProjectMemberRole
