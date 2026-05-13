from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

from app.model import Plan, User

if TYPE_CHECKING:
    from app.model import Plan, User


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    user_id: UUID = Field(foreign_key="users.id")
    user: User = Relationship(
        back_populates="subscription", sa_relationship_kwargs={"lazy": "selectin"}
    )

    plan_id: UUID = Field(foreign_key="plans.id")
    plan: Plan = Relationship(
        back_populates="subscription", sa_relationship_kwargs={"lazy": "selectin"}
    )

    stripe_customer_id: str
    stripe_subscription_id: str
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            postgresql.TIMESTAMP, default=None, nullable=True, onupdate=datetime.now
        )
    )
