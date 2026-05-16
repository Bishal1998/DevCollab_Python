from typing import List
from uuid import UUID

from fastapi import APIRouter

from app.dependency import PlanServiceDep, SubscriptionServiceDep
from app.schema import ReadPlan, ReadSubscription

router = APIRouter(prefix="/api", tags=["Subscription & Billings"])


@router.get("/plans", response_model=List[ReadPlan])
async def get_all_plans(plan_service: PlanServiceDep):
    return await plan_service.get_all_plans()


@router.get("/me/subscription", response_model=ReadSubscription)
async def get_current_subscription(subscription_service: SubscriptionServiceDep):
    return await subscription_service.get_current_subscription()


@router.post("/stripe/checkout")
async def stripe_checkout(plan_id: UUID, subscription_service: SubscriptionServiceDep):
    return await subscription_service.stripe_checkout(plan_id)


@router.post("/stripe/portal")
async def customer_portal(subscription_service: SubscriptionServiceDep):
    return await subscription_service.customer_portal()
