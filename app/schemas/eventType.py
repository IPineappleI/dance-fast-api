from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List
import uuid


class EventTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class EventTypeInfo(EventTypeCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class EventTypePage(BaseModel):
    events_types: List[EventTypeInfo]
    total: int

    class Config:
        from_attributes = True


class EventTypeFilters(BaseModel):
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class EventTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
