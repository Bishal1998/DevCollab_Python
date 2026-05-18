from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.model.user import User
from app.schema.auth_schema import Login, Signup
from app.services.base_service import BaseService
from app.utils import hash_password


class AuthService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def login(self, data: Login):
        pass

    async def signup(self, data: Signup):

        existing_user = await self.session.scalar(
            select(User).where(User.email == data.email)
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already exists with the email : {data.email}",
            )

        new_user = User(
            **data.model_dump(exclude={"password"}),
            hashed_password=hash_password(data.password),
        )

        return await self._create(new_user)

    async def profile(self, id: UUID):
        pass
