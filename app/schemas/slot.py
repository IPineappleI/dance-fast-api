from typing import Optional, List

from pydantic import BaseModel
import uuid
from datetime import time, datetime

from app.schemas.teacher import TeacherMoreInfo


class SlotBase(BaseModel):
    teacher_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time

    class Config:
        from_attributes = True


class SlotInfo(SlotBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SlotFullInfo(SlotInfo):
    teacher: TeacherMoreInfo

    class Config:
        from_attributes = True


class SlotUpdate(BaseModel):
    teacher_id: Optional[uuid.UUID] = None
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    class Config:
        from_attributes = True


class SlotSearch(BaseModel):
    date_from: datetime
    date_to: datetime

    teacher_ids: Optional[List[uuid.UUID]] = None
    lesson_type_ids: Optional[List[uuid.UUID]] = None

    class Config:
        from_attributes = True


class SlotAvailable(BaseModel):
    teacher: TeacherMoreInfo
    start_time: datetime
    finish_time: datetime

    class Config:
        from_attributes = True
