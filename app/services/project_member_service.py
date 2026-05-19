from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.model.project import Project
from app.model.project_member import ProjectMember, ProjectMemberRole
from app.model.user import User
from app.schema import InviteMember
from app.services.base_service import BaseService


class ProjectMemberService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectMember, session)

    async def _get_project(self, project_id: UUID):
        project = await self._get(Project, project_id)

        if not project or project.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id: {project_id} not found.",
            )
        return project

    async def _get_user(self, user_id: UUID):
        user = await self._get(User, user_id)

        if not user or user.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {user_id} not found.",
            )
        return user

    async def get_all_members(self, project_id: UUID):
        await self._get_project(project_id)

        result = await self.session.scalars(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )

        members = result.all()
        return members

    async def invite_by_email(self, project_id: UUID, invite_detail: InviteMember):
        await self._get_project(project_id)

        user = await self.session.scalar(
            select(User).where(User.email == invite_detail.email)
        )

        if not user:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"User not found with email : {invite_detail.email}",
            )

        existing_member = await self.session.scalar(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .where(ProjectMember.user_id == user.id)
        )

        if existing_member:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="User is already a member of this project.",
            )

        member = ProjectMember(
            user_id=user.id,
            project_id=project_id,
            role=invite_detail.role,
            ## TODO: invited_by=should be current logged in user
            invited_at=datetime.now(),
        )

        return await self._create(member)

    async def change_role(
        self, project_id: UUID, user_id: UUID, role: ProjectMemberRole
    ):
        await self._get_project(project_id)
        await self._get_user(user_id)

        project_member = await self.session.scalar(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .where(ProjectMember.user_id == user_id)
        )

        if not project_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of project {project_id}.",
            )

        if project_member.role == ProjectMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You're the owner of the project",
            )

        if role == ProjectMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign the OWNER role. Transfer ownership explicitly.",
            )

        project_member.role = role
        return await self._update(project_member)

    async def remove_member(self, project_id: UUID, user_id: UUID):
        await self._get_project(project_id)
        await self._get_user(user_id)

        project_member = await self.session.scalar(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .where(ProjectMember.user_id == user_id)
        )

        if not project_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of project {project_id}.",
            )

        if project_member.role == ProjectMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You're the owner of the project",
            )

        await self._delete(project_member)
