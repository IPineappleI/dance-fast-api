from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from app.schemas.subscription_template import SubscriptionTemplateInfo
import uuid


class SubscriptionBase(BaseModel):
    """Базовая схема шаблона подписки."""
    student_id: uuid.UUID
    subscription_template_id: uuid.UUID
    expiration_date: datetime
    payment_id: uuid.UUID

    class Config:
        from_attributes = True


class SubscriptionInfo(SubscriptionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    student_id: Optional[uuid.UUID] = None
    subscription_template_id: Optional[uuid.UUID] = None
    expiration_date: Optional[datetime] = None
    payment_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class SubscriptionFullInfo(SubscriptionInfo):
    subscription_template: SubscriptionTemplateInfo

    class Config:
        from_attributes = True
