from fastapi import APIRouter

from app.dependency import AuthServiceDep, CurrentUserDep
from app.schema.auth_schema import Login, Signup, Token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(data: Login, service: AuthServiceDep):
    return await service.login(data)


@router.post("/signup")
async def signup(data: Signup, service: AuthServiceDep):
    return await service.signup(data)


@router.get("/me")
async def profile(current_user: CurrentUserDep):
    return current_user
