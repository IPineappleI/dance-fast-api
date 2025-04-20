from typing import Optional

from pydantic import BaseModel
from datetime import datetime
import uuid

from app.schemas.payment import PaymentInfoWithType


class SubscriptionBase(BaseModel):
    student_id: uuid.UUID
    subscription_template_id: uuid.UUID
    payment_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class SubscriptionInfo(SubscriptionBase):
    id: uuid.UUID
    expiration_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    subscription_template_id: Optional[uuid.UUID] = None
    expiration_date: Optional[datetime] = None
    payment_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class SubscriptionFullInfo(SubscriptionInfo):
    subscription_template: "SubscriptionTemplateFullInfo"
    payment: Optional[PaymentInfoWithType] = None

    class Config:
        from_attributes = True


from app.schemas.subscription_template import SubscriptionTemplateFullInfo

SubscriptionFullInfo.model_rebuild()
