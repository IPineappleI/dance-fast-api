import uuid
from pydantic import BaseModel
from app.schemas.user import UserBase, UserUpdate


class AdminBase(BaseModel):
    """Базовая схема администратора."""
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class AdminInfo(AdminBase):
    id: uuid.UUID
    user: UserBase

    class Config:
        from_attributes = True


class AdminUpdate(UserUpdate):
    class Config:
        from_attributes = True

