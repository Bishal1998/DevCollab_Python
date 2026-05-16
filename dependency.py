from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.services import AuthService

sessionDep = Annotated[str, Depends(get_session)]


def get_auth_service(session: AsyncSession):
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
