from uuid import UUID

from fastapi import APIRouter

from app.dependency import ProjectServiceDep
from app.schema.ProjectSchema import CreateProject, ReadProject, UpdateProject

router = APIRouter(prefix="/project", tags=["Project"])


@router.post("/", response_model=ReadProject)
async def create(data: CreateProject, service: ProjectServiceDep):
    return await service.create(data)


@router.put("/{id}", response_model=ReadProject)
async def update(id: UUID, data: UpdateProject, service: ProjectServiceDep):
    return await service.update(id, data)


@router.get("/{id}", response_model=ReadProject)
async def get(id: UUID, service: ProjectServiceDep):
    return await service.get(id)


@router.delete("/{id}", response_model=dict)
async def delete(id: UUID, service: ProjectServiceDep):
    await service.delete(id)
    return {"detail": f"Project with id: {id} deleted successfully."}
