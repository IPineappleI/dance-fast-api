from pydantic import BaseModel
from app.schemas.level import LevelInfo
from app.schemas.association import GroupTeacherBase, GroupStudentBase
import uuid
from typing import Optional, List
from datetime import datetime


class GroupBase(BaseModel):
    """Базовая схема группы."""
    name: str
    description: Optional[str] = None
    level_id: uuid.UUID
    max_capacity: int

    class Config:
        from_attributes = True


class GroupInfo(GroupBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str | None] = None
    level_id: Optional[uuid.UUID] = None
    max_capacity: Optional[int] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class GroupFullInfo(GroupInfo):
    level: LevelInfo
    students: List[GroupStudentBase]
    teachers: List[GroupTeacherBase]

    class Config:
        from_attributes = True
