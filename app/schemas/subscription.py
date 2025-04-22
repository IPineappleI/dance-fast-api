from typing import Optional

from pydantic import BaseModel
from datetime import datetime
import uuid

from app.schemas.payment import PaymentFullInfo
from app.schemas.subscriptionTemplate import SubscriptionTemplateFullInfo


class SubscriptionBase(BaseModel):
    student_id: uuid.UUID
    subscription_template_id: uuid.UUID
    payment_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class SubscriptionInfo(SubscriptionBase):
    id: uuid.UUID
    expiration_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionFullInfo(SubscriptionInfo):
    subscription_template: SubscriptionTemplateFullInfo
    lessons_left: int
    payment: Optional[PaymentFullInfo] = None

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    subscription_template_id: Optional[uuid.UUID] = None
    expiration_date: Optional[datetime] = None
    payment_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
