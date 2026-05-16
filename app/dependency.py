from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.services import AuthService, ProjectService

sessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_auth_service(session: sessionDep):
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_project_service(session: sessionDep):
    return ProjectService(session)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
