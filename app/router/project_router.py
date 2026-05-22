from typing import List
from uuid import UUID

from fastapi import APIRouter

from app.dependency import CurrentUserDep, ProjectServiceDep
from app.schema.project_schema import CreateProject, ReadProject, UpdateProject

router = APIRouter(prefix="/project", tags=["Project"])


@router.post("/", response_model=ReadProject)
async def create(
    data: CreateProject, service: ProjectServiceDep, current_user: CurrentUserDep
):
    return await service.create(data, current_user.id)


@router.get("/my-projects", response_model=List[ReadProject])
async def get_my_projects(service: ProjectServiceDep, current_user: CurrentUserDep):
    return await service.get_my_projects(current_user.id)


@router.put("/{id}", response_model=ReadProject)
async def update(
    id: UUID,
    data: UpdateProject,
    service: ProjectServiceDep,
    current_user: CurrentUserDep,
):
    return await service.update(id, data, current_user.id)


@router.get("/{id}", response_model=ReadProject)
async def get(id: UUID, service: ProjectServiceDep):
    return await service.get(id)


@router.delete("/{id}", response_model=dict)
async def delete(id: UUID, service: ProjectServiceDep, current_user: CurrentUserDep):
    await service.delete(id, current_user.id)
    return {"detail": f"Project with id: {id} deleted successfully."}
