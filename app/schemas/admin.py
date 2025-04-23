import uuid
from datetime import datetime

from pydantic import BaseModel
from app.schemas.user import UserBase, UserUpdate, UserCreate


class AdminBase(BaseModel):
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class AdminInfo(AdminBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AdminFullInfo(AdminInfo):
    user: UserBase

    class Config:
        from_attributes = True


class AdminFullInfoWithRole(AdminFullInfo):
    role: str

    class Config:
        from_attributes = True


class AdminUpdate(UserUpdate):
    class Config:
        from_attributes = True


class AdminCreate(UserCreate):
    class Config:
        from_attributes = True
