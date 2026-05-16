from sqlalchemy.ext.asyncio import AsyncSession


class PlanService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_plans(self):
        pass
