from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.association import AssociationLessonType


class SubscriptionTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    lesson_count: int
    expiration_date: Optional[datetime] = None
    expiration_day_count: Optional[int] = None
    price: float

    class Config:
        from_attributes = True


class SubscriptionTemplateInfo(SubscriptionTemplateBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionTemplateFullInfo(SubscriptionTemplateInfo):
    lesson_types: List[AssociationLessonType]

    class Config:
        from_attributes = True


class SubscriptionTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    lesson_count: Optional[int] = None
    expiration_date: Optional[datetime] = None
    expiration_day_count: Optional[int] = None
    price: Optional[float] = None

    class Config:
        from_attributes = True
