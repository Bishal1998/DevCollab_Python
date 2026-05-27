from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.model.user import User
from app.services import (
    AuthService,
    FileService,
    PlanService,
    ProjectMemberService,
    ProjectService,
    SubscriptionService,
    UsageService,
)
from app.services.webhook_service import WebhookService
from app.utils.jwt_token import verify_access_token

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


def get_project_member_service(session: session_dep):
    return ProjectMemberService(session)


ProjectMemberServiceDep = Annotated[
    ProjectMemberService, Depends(get_project_member_service)
]


def get_subscription_service(session: session_dep):
    return SubscriptionService(session)


SubscriptionServiceDep = Annotated[
    SubscriptionService, Depends(get_subscription_service)
]


def get_plan_service(session: session_dep):
    return PlanService(session)


PlanServiceDep = Annotated[PlanService, Depends(get_plan_service)]


def get_usage_service(session: session_dep):
    return UsageService(session)


UsageServiceDep = Annotated[UsageService, Depends(get_usage_service)]

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: session_dep,
) -> User:
    payload = verify_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    user_id = payload.get("user_id")

    user = await session.get(User, UUID(user_id)) if user_id else None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_webhook_service(session: session_dep):
    return WebhookService(session)


WebhookServiceDep = Annotated[WebhookService, Depends(get_webhook_service)]
