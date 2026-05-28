import json
from typing import List

import stripe
from fastapi import APIRouter, Header, HTTPException, Request, status

from app.dependency import (
    CurrentUserDep,
    PlanServiceDep,
    SubscriptionServiceDep,
    WebhookServiceDep,
)
from app.schema import CheckoutRequest, ReadPlan, ReadSubscription
from config import stripe_settings

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
    data: CheckoutRequest,
    subscription_service: SubscriptionServiceDep,
    plan_service: PlanServiceDep,
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


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    service: WebhookServiceDep,
    stripe_signature: str = Header(alias="stripe-signature"),
):
    raw_body = await request.body()

    ## verify signature

    try:
        stripe.Webhook.construct_event(
            payload=raw_body,
            sig_header=stripe_signature,
            secret=stripe_settings.STRIPE_WEBHOOK_SECRET,
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe Signature"
        )

    raw_event = json.loads(raw_body)
    event_type = raw_event["type"]
    event_dict = raw_event["data"]["object"]

    if event_type == "checkout.session.completed":
        await service.handle_checkout_completed(event_dict)

    elif event_type == "customer.subscription.updated":
        await service.handle_subscription_updated(event_dict)

    elif event_type == "customer.subscription.deleted":
        await service.handle_subscription_deleted(event_dict)

    elif event_type == "invoice.payment_failed":
        await service.handle_payment_failed(event_dict)

    return {"received": True}
