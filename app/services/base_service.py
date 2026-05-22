from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from app.model import ProjectMember
from app.model.project_member import ProjectMemberRole


class BaseService:
    def __init__(self, model: type[SQLModel], session: AsyncSession):
        self.model = model
        self.session = session

    async def _create(self, data: SQLModel):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def _get_all(self):
        result = await self.session.scalars(select(self.model))
        return result.all()

    async def _get(self, id: UUID):
        return await self.session.get(self.model, id)

    async def _update(self, data: SQLModel):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def _delete(self, model: SQLModel):
        await self.session.delete(model)
        await self.session.commit()

    async def _check_project_owner(self, project_id: UUID, user_id: UUID):
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

        return project_member
