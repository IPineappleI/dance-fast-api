from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.lessonType import LessonTypeFullInfo


class SubscriptionTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    lesson_count: int
    expiration_date: Optional[datetime] = None
    expiration_day_count: Optional[int] = None
    price: float

    class Config:
        from_attributes = True


class SubscriptionTemplateInfo(SubscriptionTemplateCreate):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionTemplateFullInfo(SubscriptionTemplateInfo):
    lesson_types: List[LessonTypeFullInfo]

    class Config:
        from_attributes = True


class SubscriptionTemplatePage(BaseModel):
    subscription_templates: List[SubscriptionTemplateInfo]
    total: int

    class Config:
        from_attributes = True


class SubscriptionTemplateFullInfoPage(BaseModel):
    subscription_templates: List[SubscriptionTemplateFullInfo]
    total: int

    class Config:
        from_attributes = True


class SubscriptionTemplateSearch(BaseModel):
    lesson_type_ids: Optional[List[uuid.UUID]] = None
    dance_style_ids: Optional[List[uuid.UUID]] = None
    is_expired: Optional[bool] = None

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
