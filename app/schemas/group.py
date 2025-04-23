from datetime import datetime

from pydantic import BaseModel

from app.schemas.level import LevelInfo
import uuid
from typing import Optional, List


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    level_id: uuid.UUID
    max_capacity: int

    class Config:
        from_attributes = True


class GroupInfo(GroupBase):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class GroupMoreInfo(GroupInfo):
    level: LevelInfo

    class Config:
        from_attributes = True


class GroupFullInfo(GroupMoreInfo):
    students: List["StudentMoreInfo"]
    teachers: List["TeacherMoreInfo"]

    class Config:
        from_attributes = True


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level_id: Optional[uuid.UUID] = None
    max_capacity: Optional[int] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


from app.schemas.student import StudentMoreInfo
from app.schemas.teacher import TeacherMoreInfo

GroupFullInfo.model_rebuild()
