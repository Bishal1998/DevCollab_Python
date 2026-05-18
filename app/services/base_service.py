from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select


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
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def _get(self, id: UUID):
        return await self.session.get(self.model, id)

    async def _update(self, data: SQLModel):
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def _delete(self, model: SQLModel):
        await self.session.delete(model)
        await self.session.commit()
