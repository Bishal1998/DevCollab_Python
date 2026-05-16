from fastapi import APIRouter

from app.router.AuthRouter import router as AuthRouter
from app.router.ProjectRouter import router as ProjectRouter

master_router = APIRouter()

master_router.include_router(AuthRouter)
master_router.include_router(ProjectRouter)
