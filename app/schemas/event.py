import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.eventType import EventTypeInfo


class EventBase(BaseModel):
    """Базовая схема мероприятия."""
    event_type_id: uuid.UUID
    name: str
    description: str | None = None
    start_time: datetime
    photo_url: str

    class Config:
        from_attributes = True


class EventInfo(EventBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class EventUpdate(BaseModel):
    event_type_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    description: Optional[str | None] = None
    start_time: Optional[datetime] = None
    photo_url: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class EventFullInfo(EventInfo):
    event_type: EventTypeInfo

    class Config:
        from_attributes = True
