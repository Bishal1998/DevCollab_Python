from fastapi import APIRouter

from app.router.AuthRouter import router as AuthRouter

master_router = APIRouter()

master_router.include_router(AuthRouter)
