import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.group import GroupMoreInfo
from app.schemas.lessonType import LessonTypeFullInfo
from app.schemas.user import UserBase, UserUpdate, UserCreate


class TeacherBase(BaseModel):
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class TeacherInfo(TeacherBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class TeacherMoreInfo(TeacherInfo):
    user: UserBase
    lesson_types: List[LessonTypeFullInfo]

    class Config:
        from_attributes = True


class TeacherFullInfo(TeacherMoreInfo):
    groups: List[GroupMoreInfo]

    class Config:
        from_attributes = True


class TeacherFullInfoWithRole(TeacherFullInfo):
    role: str

    class Config:
        from_attributes = True


class TeacherUpdate(UserUpdate):
    class Config:
        from_attributes = True


class TeacherCreate(UserCreate):
    class Config:
        from_attributes = True
