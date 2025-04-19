import uuid
from pydantic import BaseModel

from app.schemas.user import UserBase, UserCreate, UserUpdate
from app.schemas.level import LevelInfo
from typing import List, Optional
from app.schemas.association import MemberGroupBase
from app.schemas.subscription import SubscriptionFullInfo


class StudentBase(BaseModel):
    """Базовая схема студента."""
    user_id: uuid.UUID
    level_id: uuid.UUID

    class Config:
        from_attributes = True


class StudentInfo(StudentBase):
    id: uuid.UUID
    user: UserBase
    level: LevelInfo

    class Config:
        from_attributes = True


class StudentUpdate(UserUpdate):
    level_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class StudentFullInfo(StudentInfo):
    groups: List[MemberGroupBase]
    subscriptions: List[SubscriptionFullInfo]

    class Config:
        from_attributes = True


class StudentCreate(UserCreate):
    level_id: uuid.UUID

    class Config:
        from_attributes = True
