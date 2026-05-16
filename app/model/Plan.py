from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.model import Subscription


class Plan(SQLModel, table=True):
    __tablename__ = "plans"

    id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, default=uuid4))
    name: str = Field(nullable=False)
    stripe_price_id: str
    max_projects: int
    max_tokens_per_day: int
    max_previews: int
    unlimited_ai: bool = Field(default=False)
    active: bool

    subscription: List["Subscription"] = Relationship(
        back_populates="plan", sa_relationship_kwargs={"lazy": "selectin"}
    )
