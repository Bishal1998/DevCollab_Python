from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.model.project import Project
from app.model.project_member import ProjectMember, ProjectMemberRole
from app.schema import InviteMember


class ProjectMemberService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_members(self, project_id: UUID):
        project = await self.session.get(Project, project_id)

        if not project or project.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id: {project_id} not found.",
            )

        result = await self.session.scalars(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )

        members = result.all()
        return members

    async def invite_by_email(self, project_id, invite_detail: InviteMember):
        pass

    async def change_role(
        self, project_id: UUID, user_id: UUID, role: ProjectMemberRole
    ):
        pass

    async def remove_member(self, project_id: UUID, user_id: UUID):
        pass
