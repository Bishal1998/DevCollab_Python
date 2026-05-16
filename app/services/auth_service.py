from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.auth_schema import Login, Signup


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def login(self, data: Login):
        pass

    async def signup(self, data: Signup):
        pass

    async def profile(self, id: UUID):
        pass
