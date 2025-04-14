import uuid
from pydantic import BaseModel
from app.schemas.user import UserBase, UserCreate
from app.schemas.level import LevelInfo
from typing import List, Optional


class StudentBase(BaseModel):
    """Базовая схема студента."""
    user_id: uuid.UUID
    level_id: uuid.UUID

    class Config:
        from_attributes = True


class StudentInfo(StudentBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    level_id: Optional[uuid.UUID] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class StudentGroupInfo(StudentInfo):
    user: UserBase
    level: LevelInfo

    class Config:
        from_attributes = True


class StudentFullInfo(StudentInfo):
    user: UserBase
    level: LevelInfo
    groups: "List[MemberGroupBase]"

    class Config:
        from_attributes = True


class StudentCreate(UserCreate):
    level_id: uuid.UUID

    class Config:
        from_attributes = True


class StudentResponse(UserBase):
    level_name: str

    class Config:
        from_attributes = True


from app.schemas.association import MemberGroupBase

StudentFullInfo.model_rebuild()
