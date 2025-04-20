import uuid
from typing import List
from pydantic import BaseModel
from app.schemas.user import UserBase, UserUpdate
from app.schemas.association import MemberGroupBase, TeacherLessonTypeBase


class TeacherBase(BaseModel):
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class TeacherInfo(TeacherBase):
    id: uuid.UUID
    user: UserBase

    class Config:
        from_attributes = True


class TeacherUpdate(UserUpdate):
    class Config:
        from_attributes = True


class TeacherWithLessonTypes(TeacherInfo):
    lesson_types: List[TeacherLessonTypeBase]

    class Config:
        from_attributes = True


class TeacherFullInfo(TeacherInfo):
    groups: List[MemberGroupBase]
    lesson_types: List[TeacherLessonTypeBase]

    class Config:
        from_attributes = True
