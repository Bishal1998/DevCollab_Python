from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.dependency import CurrentUserDep, PlanServiceDep, SubscriptionServiceDep
from app.schema import ReadPlan, ReadSubscription
from app.schema.plan_schema import CheckoutRequest

router = APIRouter(prefix="/api", tags=["Subscription & Billings"])


@router.get("/plans", response_model=List[ReadPlan])
async def get_all_plans(plan_service: PlanServiceDep):
    return await plan_service.get_all_plans()


@router.get("/me/subscription", response_model=ReadSubscription)
async def get_current_subscription(
    subscription_service: SubscriptionServiceDep,
    current_user: CurrentUserDep,
):
    return await subscription_service.get_current_subscription(current_user.id)


@router.post("/stripe/checkout")
async def stripe_checkout(
    plan_id: UUID,
    subscription_service: SubscriptionServiceDep,
    plan_service: PlanServiceDep,
    data: CheckoutRequest,
    current_user: CurrentUserDep,
):

    plan = await plan_service.get_plan(data.plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan not found with id: {data.plan_id}",
        )
    return await subscription_service.stripe_checkout(current_user, plan)


@router.post("/stripe/portal")
async def customer_portal(
    subscription_service: SubscriptionServiceDep, current_user: CurrentUserDep
):
    return await subscription_service.customer_portal(current_user)
