from typing import Optional

from pydantic import BaseModel
import uuid


class LessonTypeBase(BaseModel):
    """Базовая схема типа платежа."""
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class LessonTypeInfo(LessonTypeBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class LessonTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
