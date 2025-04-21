from datetime import datetime
from typing import Optional

from pydantic import BaseModel
import uuid


class LevelBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class LevelInfo(LevelBase):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class LevelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
