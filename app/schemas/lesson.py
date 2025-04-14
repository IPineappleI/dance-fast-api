from pydantic import BaseModel
from app.schemas.group import GroupFullInfo
from app.schemas.lesson_type import LessonTypeInfo
from app.schemas.classroom import ClassroomInfo
from app.schemas.association import GroupTeacherBase, GroupStudentBase
import uuid
from typing import Optional, List
from datetime import datetime


class LessonBase(BaseModel):
    """Базовая схема группы."""
    name: str
    description: Optional[str] = None
    lesson_type_id: uuid.UUID
    start_time: datetime
    finish_time: datetime
    classroom_id: uuid.UUID
    group_id: uuid.UUID

    class Config:
        from_attributes = True


class LessonInfo(LessonBase):
    id: uuid.UUID
    is_confirmed: bool
    are_neighbours_allowed: bool
    terminated: bool

    class Config:
        from_attributes = True


class LessonUpdate(LessonBase):
    name: Optional[str] = None
    description: Optional[str] = None
    lesson_type_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    classroom_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None
    is_confirmed: Optional[bool] = None
    are_neighbours_allowed: Optional[bool] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class LessonFullInfo(LessonInfo):
    lesson_type: LessonTypeInfo
    classroom: ClassroomInfo
    group: GroupFullInfo

    class Config:
        from_attributes = True
