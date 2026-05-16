from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_current_subscription(self):
        pass

    async def stripe_checkout(self, plan_id: UUID):
        pass

    async def customer_portal(self):
        pass
