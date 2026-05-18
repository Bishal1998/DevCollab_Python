from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.model.subscription import SubscriptionStatus


class ReadSubscription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    plan_id: UUID
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: Optional[datetime]
