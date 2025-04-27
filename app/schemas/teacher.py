import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.group import GroupMoreInfo
from app.schemas.lessonType import LessonTypeFullInfo
from app.schemas.user import UserInfo, UserUpdate, UserCreate, UserFilters


class TeacherInfo(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class TeacherMoreInfo(TeacherInfo):
    user: UserInfo
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


class TeacherPage(BaseModel):
    teachers: List[TeacherInfo]
    total: int

    class Config:
        from_attributes = True


class TeacherFullInfoPage(BaseModel):
    teachers: List[TeacherFullInfo]
    total: int

    class Config:
        from_attributes = True


class TeacherCreate(UserCreate):
    class Config:
        from_attributes = True


class TeacherFilters(UserFilters):
    group_ids: Optional[List[uuid.UUID]] = None
    lesson_type_ids: Optional[List[uuid.UUID]] = None

    class Config:
        from_attributes = True


class TeacherUpdate(UserUpdate):
    class Config:
        from_attributes = True
