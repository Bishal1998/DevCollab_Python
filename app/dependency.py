from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.services import AuthService, FileService, ProjectService

session_dep = Annotated[AsyncSession, Depends(get_session)]


def get_auth_service(session: session_dep):
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_project_service(session: session_dep):
    return ProjectService(session)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


def get_file_service(session: session_dep):
    return FileService(session)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
