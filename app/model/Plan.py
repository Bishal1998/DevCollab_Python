from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Subscription


class Plan(SQLModel, table=True):
    __tablename__ = "plans"

    id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, default=uuid4))
    name: str = Field(sa_column=Column(String, nullable=False))
    stripe_product_id: str = Field(
        sa_column=Column(String, nullable=False, unique=True)
    )
    stripe_price_id: str = Field(sa_column=Column(String, nullable=False, unique=True))

    max_projects: Optional[int] = Field(default=None)  # None = unlimited
    max_tokens_per_day: Optional[int] = Field(default=None)
    max_previews: Optional[int] = Field(default=None)

    unlimited_ai: bool = Field(sa_column=Column(Boolean, nullable=False, default=False))
    active: bool = Field(sa_column=Column(Boolean, nullable=False, default=True))

    subscription: List["Subscription"] = Relationship(
        back_populates="plan", sa_relationship_kwargs={"lazy": "selectin"}
    )
