from typing import Optional

from pydantic import BaseModel
import uuid

from app.schemas.dance_style import DanceStyleInfo


class LessonTypeBase(BaseModel):
    dance_style_id: uuid.UUID
    is_group: bool

    class Config:
        from_attributes = True


class LessonTypeInfo(LessonTypeBase):
    id: uuid.UUID
    dance_style: DanceStyleInfo
    terminated: bool

    class Config:
        from_attributes = True


class LessonTypeUpdate(BaseModel):
    dance_style_id: Optional[uuid.UUID] = None
    is_group: Optional[bool] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
