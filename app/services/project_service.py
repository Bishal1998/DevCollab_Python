from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.model import Project, ProjectMember
from app.model.project_member import ProjectMemberRole
from app.schema.project_schema import CreateProject, UpdateProject
from app.services import BaseService


class ProjectService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def create(self, data: CreateProject, current_user: UUID):

        new_project = Project(**data.model_dump())

        await self._create(new_project)

        owner = ProjectMember(
            user_id=current_user,
            project_id=new_project.id,
            role=ProjectMemberRole.OWNER,
        )

        await self._create(owner)

        return new_project

    async def get(self, id: UUID):
        project = await self._get(id)

        if not project or project.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id: {id} not found.",
            )

        return project

    async def update(self, id: UUID, data: UpdateProject, current_user: UUID):
        project = await self.get(id)
        await self.check_project_owner(id, current_user)

        updated_data = data.model_dump(exclude_none=True)

        for k, v in updated_data.items():
            setattr(project, k, v)

        return await self._update(project)

    async def delete(self, id: UUID, current_user: UUID):
        project = await self.get(id)
        await self.check_project_owner(id, current_user)

        project.deleted_at = datetime.now(timezone.utc)

        await self._update(project)

    async def check_project_owner(self, project_id: UUID, user_id: UUID):
        project_member = await self.session.scalar(
            select(ProjectMember).where(
                ProjectMember.user_id == user_id,
                ProjectMember.project_id == project_id,
            )
        )

        if not project_member or project_member.role != ProjectMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can perform this action.",
            )
