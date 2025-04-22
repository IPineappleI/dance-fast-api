import uuid
from typing import Optional, List

from pydantic import BaseModel
from datetime import date


class SubscriptionPurchasesFilters(BaseModel):
    date_from: date
    date_to: date
    interval_in_days: int
    is_group: Optional[bool] = None
    dance_style_ids: Optional[List[uuid.UUID]] = None
    subscription_template_ids: Optional[List[uuid.UUID]] = None

    class Config:
        from_attributes = True


class SubscriptionPurchasesInterval(BaseModel):
    date_from: date
    date_to: date
    count: int
    sum: float

    class Config:
        from_attributes = True
