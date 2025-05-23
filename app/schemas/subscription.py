from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime
import uuid

from app.schemas.subscriptionTemplate import SubscriptionTemplateFullInfo


class SubscriptionInfo(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    subscription_template_id: uuid.UUID
    payment_id: Optional[uuid.UUID] = None
    expiration_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionMoreInfo(SubscriptionInfo):
    subscription_template: SubscriptionTemplateFullInfo
    lessons_left: int

    class Config:
        from_attributes = True


class SubscriptionFullInfo(SubscriptionMoreInfo):
    payment: Optional['PaymentInfo'] = None

    class Config:
        from_attributes = True


class SubscriptionPage(BaseModel):
    subscriptions: List[SubscriptionInfo]
    total: int

    class Config:
        from_attributes = True


class SubscriptionFullInfoPage(BaseModel):
    subscriptions: List[SubscriptionFullInfo]
    total: int

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    student_id: uuid.UUID
    subscription_template_id: uuid.UUID
    payment_id: uuid.UUID

    class Config:
        from_attributes = True


class SubscriptionFilters(BaseModel):
    student_id: Optional[uuid.UUID] = None
    subscription_template_ids: Optional[List[uuid.UUID]] = None
    is_paid: Optional[bool] = None
    is_expired: Optional[bool] = None

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    subscription_template_id: Optional[uuid.UUID] = None
    expiration_date: Optional[datetime] = None
    payment_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


from app.schemas.payment import PaymentInfo

SubscriptionFullInfo.model_rebuild()
