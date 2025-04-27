import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel
from app.schemas.user import UserInfo, UserUpdate, UserCreate, UserFilters


class AdminInfo(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AdminFullInfo(AdminInfo):
    user: UserInfo

    class Config:
        from_attributes = True


class AdminFullInfoWithRole(AdminFullInfo):
    role: str

    class Config:
        from_attributes = True


class AdminPage(BaseModel):
    admins: List[AdminInfo]
    total: int

    class Config:
        from_attributes = True


class AdminFullInfoPage(BaseModel):
    admins: List[AdminFullInfo]
    total: int

    class Config:
        from_attributes = True


class AdminCreate(UserCreate):
    class Config:
        from_attributes = True


class AdminFilters(UserFilters):
    class Config:
        from_attributes = True


class AdminUpdate(UserUpdate):
    class Config:
        from_attributes = True
