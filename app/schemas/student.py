import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.group import GroupMoreInfo
from app.schemas.user import UserInfo, UserCreate, UserUpdate, UserFilters
from app.schemas.level import LevelInfo
from typing import List, Optional
from app.schemas.subscription import SubscriptionFullInfo


class StudentInfo(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    level_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class StudentMoreInfo(StudentInfo):
    user: UserInfo
    level: LevelInfo

    class Config:
        from_attributes = True


class StudentFullInfo(StudentMoreInfo):
    groups: List[GroupMoreInfo]
    subscriptions: List[SubscriptionFullInfo]

    class Config:
        from_attributes = True


class StudentFullInfoWithRole(StudentFullInfo):
    role: str

    class Config:
        from_attributes = True


class StudentPage(BaseModel):
    students: List[StudentInfo]
    total: int

    class Config:
        from_attributes = True


class StudentFullInfoPage(BaseModel):
    students: List[StudentFullInfo]
    total: int

    class Config:
        from_attributes = True


class StudentCreate(UserCreate):
    level_id: uuid.UUID

    class Config:
        from_attributes = True


class StudentFilters(UserFilters):
    level_ids: Optional[List[uuid.UUID]] = None
    group_ids: Optional[List[uuid.UUID]] = None

    class Config:
        from_attributes = True


class StudentUpdate(UserUpdate):
    level_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
