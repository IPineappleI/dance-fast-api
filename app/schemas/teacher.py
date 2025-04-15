import uuid
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import UserBase
from app.schemas.association import MemberGroupBase, TeacherLessonTypeBase


class TeacherBase(BaseModel):
    """Базовая схема преподавателя."""
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class TeacherInfo(TeacherBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class TeacherUpdate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class TeacherGroupInfo(TeacherInfo):
    user: UserBase

    class Config:
        from_attributes = True


class TeacherLessonInfo(TeacherInfo):
    user: UserBase

    class Config:
        from_attributes = True


class TeacherFullInfo(TeacherInfo):
    user: UserBase
    groups: List[MemberGroupBase]
    lesson_types: List[TeacherLessonTypeBase]

    class Config:
        from_attributes = True
