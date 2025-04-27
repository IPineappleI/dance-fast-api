from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
import uuid

from app.schemas.danceStyle import DanceStyleInfo


class LessonTypeCreate(BaseModel):
    dance_style_id: uuid.UUID
    is_group: bool

    class Config:
        from_attributes = True


class LessonTypeInfo(LessonTypeCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class LessonTypeFullInfo(LessonTypeInfo):
    dance_style: DanceStyleInfo

    class Config:
        from_attributes = True


class LessonTypePage(BaseModel):
    lesson_types: List[LessonTypeInfo]
    total: int

    class Config:
        from_attributes = True


class LessonTypeFullInfoPage(BaseModel):
    lesson_types: List[LessonTypeFullInfo]
    total: int

    class Config:
        from_attributes = True


class LessonTypeFilters(BaseModel):
    dance_style_ids: Optional[List[uuid.UUID]] = None
    is_group: Optional[bool] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class LessonTypeUpdate(BaseModel):
    dance_style_id: Optional[uuid.UUID] = None
    is_group: Optional[bool] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
