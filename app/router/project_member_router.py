from typing import List
from uuid import UUID

from fastapi import APIRouter

from app.dependency import ProjectMemberServiceDep
from app.model.project_member import ProjectMemberRole
from app.schema import InviteMember, ReadProjectMember

router = APIRouter(prefix="/api/projects", tags=["Project Member"])


@router.get("/{project_id}/members", response_model=List[ReadProjectMember])
async def get_all_members(project_id: UUID, service: ProjectMemberServiceDep):
    return await service.get_all_members(project_id)


@router.post("/{project_id}/members")
async def invite_members(
    project_id: UUID, invite_detail: InviteMember, service: ProjectMemberServiceDep
):
    return await service.invite_by_email(project_id, invite_detail)


@router.patch("/{project_id}/members/{user_id}", response_model=ReadProjectMember)
async def change_role(
    project_id: UUID,
    user_id: UUID,
    role: ProjectMemberRole,
    service: ProjectMemberServiceDep,
):
    return await service.change_role(project_id, user_id, role)


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    service: ProjectMemberServiceDep,
):
    return await service.remove_member(project_id, user_id)
