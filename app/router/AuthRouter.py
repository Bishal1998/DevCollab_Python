from uuid import UUID

from fastapi import APIRouter

from app.dependency import AuthServiceDep
from app.schema.AuthSchema import Login, Signup

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login")
async def login(data: Login, service: AuthServiceDep):
    return await service.login(data)


@router.post("/signup")
async def signup(data: Signup, service: AuthServiceDep):
    return await service.signup(data)


@router.get("/me")
async def profile(id: UUID, service: AuthServiceDep):
    return await service.profile(id)
