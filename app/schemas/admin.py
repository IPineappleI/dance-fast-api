import uuid
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserBase


class AdminBase(BaseModel):
    """Базовая схема администратора."""
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class AdminInfo(AdminBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class AdminUpdate(BaseModel):
    user_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class AdminFullInfo(AdminInfo):
    user: UserBase

    class Config:
        from_attributes = True
