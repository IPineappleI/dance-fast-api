import uuid
from pydantic import BaseModel
from typing import Optional


class ClassroomBase(BaseModel):
    """Базовая схема зала."""
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class ClassroomInfo(ClassroomBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str | None] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
