from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.project_member import ProjectMemberRole


class ProjectMemberService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_members(self, project_id: UUID):
        pass

    async def invite_by_email(self, project_id, email: EmailStr):
        pass

    async def change_role(
        self, project_id: UUID, user_id: UUID, role: ProjectMemberRole
    ):
        pass

    async def remove_member(self, project_id: UUID, user_id: UUID):
        pass
