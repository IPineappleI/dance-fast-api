import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class ClassroomBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ClassroomInfo(ClassroomBase):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class ClassroomSearch(BaseModel):
    date_from: datetime
    date_to: datetime

    class Config:
        from_attributes = True
