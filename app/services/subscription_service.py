from uuid import UUID

import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import desc, select

from app.model import Subscription
from app.model.plan import Plan
from app.model.subscription import SubscriptionStatus
from app.model.user import User
from app.services.base_service import BaseService
from config import stripe_settings

stripe.api_key = stripe_settings.STRIPE_SECRET_KEY


class SubscriptionService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_current_subscription(self, user_id: UUID):
        subscription = await self.session.scalar(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status != SubscriptionStatus.CANCELED)
            .order_by(desc(Subscription.created_at))
        )

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found",
            )

        return subscription

    async def stripe_checkout(self, user: User, plan: Plan):
        try:
            if user.stripe_customer_id:
                customer_id = user.stripe_customer_id
            else:
                customer = await stripe.Customer.create_async(
                    email=user.email, metadata={"user_id": str(user.id)}
                )
                customer_id = customer.id

                user.stripe_customer_id = customer_id
                await self._update(user)

            checkout_session = await stripe.checkout.Session.create_async(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
                mode="subscription",
                success_url=f"{stripe_settings.DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{stripe_settings.DOMAIN}/cancel",
                metadata={"user_id": str(user.id), "plan_id": str(plan.id)},
            )

            return {"checkout_url": checkout_session.url}
        except stripe.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.user_message
            )

    async def customer_portal(self, user: User):
        if not user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No billing account found for this user.",
            )

        try:
            portal_session = await stripe.billing_portal.Session.create_async(
                customer=user.stripe_customer_id,
                return_url=f"{stripe_settings.DOMAIN}/dashboard",
            )
            return {"portal_url": portal_session.url}

        except stripe.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.user_message,
            )
