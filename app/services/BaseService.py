from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel


class BaseService:
    def __init__(self, model: SQLModel, session: AsyncSession):
        self.model = model
        self.session = session

    async def _create(self, data: SQLModel):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def _get_all(self):
        return self.session.get()

    async def _get(self, id: UUID):
        return await self.session.get(self.model, id)

    async def _update(self, data: SQLModel):
        return self._create(data)

    async def _delete(self, model: SQLModel):
        await self.session.delete(model)
