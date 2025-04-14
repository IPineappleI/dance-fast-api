from typing import Optional

from pydantic import BaseModel
from datetime import datetime
import uuid


class LevelBase(BaseModel):
    """Базовая схема уровня."""
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class LevelInfo(LevelBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class LevelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
