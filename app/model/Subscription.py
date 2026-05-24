from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Plan, User


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"  # fixed typo
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, default=uuid4))

    user_id: UUID = Field(foreign_key="users.id")
    plan_id: UUID = Field(foreign_key="plans.id")

    stripe_customer_id: str = Field(
        sa_column=Column(String, nullable=False, index=True)
    )
    stripe_subscription_id: str = Field(
        sa_column=Column(String, nullable=False, unique=True)
    )

    status: SubscriptionStatus = Field(default=SubscriptionStatus.INCOMPLETE)
    current_period_start: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, nullable=False)
    )
    current_period_end: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, nullable=False)
    )
    cancel_at_period_end: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False)
    )
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=None,
            nullable=True,
            onupdate=datetime.now,
        )
    )

    user: Optional["User"] = Relationship(
        back_populates="subscription", sa_relationship_kwargs={"lazy": "selectin"}
    )
    plan: Optional["Plan"] = Relationship(
        back_populates="subscription", sa_relationship_kwargs={"lazy": "selectin"}
    )
