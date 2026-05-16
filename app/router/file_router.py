from typing import List
from uuid import UUID

from fastapi import APIRouter

from app.dependency import FileServiceDep
from app.schema import ReadFile

router = APIRouter(prefix="/projects", tags=["Files"])


@router.get("/{project_id}/files", response_model=List[ReadFile])
async def get_files(project_id: UUID, service: FileServiceDep):
    return await service.get_files(project_id)


@router.get("/{project_id}/files/{path:path}")
async def get_file(project_id: UUID, path: str, service: FileServiceDep):
    return await service.single_file(project_id, path)
