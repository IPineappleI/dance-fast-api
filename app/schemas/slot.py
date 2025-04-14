from typing import Optional

from pydantic import BaseModel
import uuid
from datetime import time


class SlotBase(BaseModel):
    """Базовая схема слота."""
    teacher_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time

    class Config:
        from_attributes = True


class SlotInfo(SlotBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class SlotUpdate(BaseModel):
    teacher_id: Optional[uuid.UUID] = None
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    class Config:
        from_attributes = True
