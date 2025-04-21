import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.association import GroupForLists, LessonTypeForLists
from app.schemas.user import UserBase, UserUpdate


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
    lesson_types: List[LessonTypeForLists]

    class Config:
        from_attributes = True


class TeacherFullInfo(TeacherMoreInfo):
    groups: List[GroupForLists]

    class Config:
        from_attributes = True


class TeacherUpdate(UserUpdate):
    class Config:
        from_attributes = True
