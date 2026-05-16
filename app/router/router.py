from fastapi import APIRouter

from app.router.auth_router import router as AuthRouter
from app.router.file_router import router as FileRouter
from app.router.project_member_router import router as ProjectMemberRouter
from app.router.project_router import router as ProjectRouter

master_router = APIRouter()

master_router.include_router(AuthRouter)
master_router.include_router(ProjectRouter)
master_router.include_router(FileRouter)
master_router.include_router(ProjectMemberRouter)
