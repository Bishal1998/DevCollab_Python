from fastapi import APIRouter

from app.dependency import UsageServiceDep
from app.schema import ReadPlan, ReadTodayUsage

router = APIRouter(prefix="/api/usage", tags=["Usage & Quotas"])


@router.get("/today", response_model=ReadTodayUsage)
async def tokens_used(service: UsageServiceDep):
    return await service.tokens_used()


@router.get("/limits", response_model=ReadPlan)
async def current_limits(service: UsageServiceDep):
    return await service.current_limits()
