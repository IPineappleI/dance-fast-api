import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List


class ClassroomCreate(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ClassroomInfo(ClassroomCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class ClassroomPage(BaseModel):
    classrooms: List[ClassroomInfo]
    total: int

    class Config:
        from_attributes = True


class ClassroomFilters(BaseModel):
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class ClassroomAvailableFilters(BaseModel):
    date_from: datetime
    date_to: datetime
    are_neighbours_allowed: bool

    class Config:
        from_attributes = True


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
