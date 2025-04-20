from pydantic import BaseModel
from typing import Optional
import uuid


class EventTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class EventTypeInfo(EventTypeBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class EventTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
