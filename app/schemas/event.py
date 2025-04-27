import uuid
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.schemas.eventType import EventTypeInfo


class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    event_type_id: uuid.UUID
    start_time: datetime
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class EventInfo(EventCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class EventFullInfo(EventInfo):
    event_type: EventTypeInfo

    class Config:
        from_attributes = True


class EventPage(BaseModel):
    events: List[EventInfo]
    total: int

    class Config:
        from_attributes = True


class EventFullInfoPage(BaseModel):
    events: List[EventFullInfo]
    total: int

    class Config:
        from_attributes = True


class EventFilters(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_string: Optional[str] = None
    event_type_ids: Optional[List[uuid.UUID]] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_type_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    photo_url: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
