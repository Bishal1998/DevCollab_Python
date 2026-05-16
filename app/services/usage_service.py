from sqlalchemy.ext.asyncio import AsyncSession


class UsageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def tokens_used(self):
        pass

    async def current_limits(self):
        pass
