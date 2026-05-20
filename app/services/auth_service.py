from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.model.user import User
from app.schema.auth_schema import Login, Signup, Token
from app.services.base_service import BaseService
from app.utils import hash_password, verify_password
from app.utils.jwt_token import generate_access_token


class AuthService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def login(self, data: Login):
        existing_user = await self.session.scalar(
            select(User).where(User.email == data.email)
        )

        if not existing_user or not verify_password(
            data.password, existing_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user credentials",
            )

        token = generate_access_token(token={"user_id": str(existing_user.id)})
        return Token(access_token=token)

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
