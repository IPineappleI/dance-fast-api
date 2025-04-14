from pydantic import BaseModel
from typing import Optional
import uuid


class EventTypeBase(BaseModel):
    """Базовая схема типа мероприятия."""
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class EventTypeInfo(EventTypeBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class EventTypeUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str | None] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
