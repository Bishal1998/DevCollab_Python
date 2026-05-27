from datetime import datetime

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.model.subscription import Subscription, SubscriptionStatus
from config import stripe_settings

stripe.api_key = stripe_settings.STRIPE_SECRET_KEY


class WebhookService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle_checkout_completed(self, event_data: dict):
        ## get metada
        metadata = event_data.get("metadata", {})

        user_id = metadata.get("user_id")
        plan_id = metadata.get("plan_id")

        stripe_customer_id = event_data.get("customer")
        stripe_subscription_id = event_data.get("subscription")

        if not all([user_id, plan_id, stripe_customer_id, stripe_subscription_id]):
            return

        ## fetch full subscription details from stripe
        stripe_sub = await stripe.Subscription.retrieve_async(stripe_subscription_id)

        ## create subscription row in db
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            status=SubscriptionStatus(stripe_sub["status"]),
            current_period_start=datetime.fromtimestamp(
                stripe_sub["current_period_start"]
            ),
            current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"]),
            cancel_at_period_end=stripe_sub["cancel_at_period_end"],
        )
        self.session.add(subscription)
        await self.session.commit()

    async def handle_subscription_updated(self, event_data: dict):
        stripe_subscription_id = event_data.get("id")

        subscription = await self.session.scalar(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        )

        if not subscription:
            return

        subscription.status = SubscriptionStatus(event_data["status"])
        subscription.current_period_start = datetime.fromtimestamp(
            event_data["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            event_data["current_period_end"]
        )
        subscription.cancel_at_period_end = event_data["cancel_at_period_end"]

        self.session.add(subscription)
        await self.session.commit()

    async def handle_subscription_deleted(self, event_data: dict):
        stripe_subscription_id = event_data.get("id")

        subscription = await self.session.scalar(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        )

        if not subscription:
            return

        subscription.status = SubscriptionStatus.CANCELED
        self.session.add(subscription)
        await self.session.commit()

    async def handle_payment_failed(self, event_data: dict):
        stripe_subscription_id = event_data.get("subscription")

        if not stripe_subscription_id:
            return

        subscription = await self.session.scalar(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        )

        if not subscription:
            return

        subscription.status = SubscriptionStatus.PAST_DUE
        self.session.add(subscription)
        await self.session.commit()
