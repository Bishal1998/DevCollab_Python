from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.model import Project, ProjectMember
from app.model.project_member import ProjectMemberRole
from app.schema.project_schema import CreateProject, UpdateProject
from app.services import BaseService


class ProjectService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def create(self, data: CreateProject):

        new_project = Project(**data.model_dump())

        await self._create(new_project)

        owner = ProjectMember(
            user_id=UUID("b2b290c0-2a60-4a27-b94e-806b4677127d"),
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

    async def update(self, id: UUID, data: UpdateProject):
        project = await self.get(id)

        updated_data = data.model_dump(exclude_none=True)

        for k, v in updated_data.items():
            setattr(project, k, v)

        return await self._update(project)

    async def delete(self, id: UUID):
        project = await self.get(id)

        project.deleted_at = datetime.now()

        await self._update(project)
