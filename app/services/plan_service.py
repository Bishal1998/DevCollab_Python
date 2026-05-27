from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.model import Plan
from app.services.base_service import BaseService


class PlanService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(Plan, session)

    async def get_all_plans(self):
        return await self._get_all()

    async def get_plan(self, plan_id: UUID):
        return await self._get(plan_id)
