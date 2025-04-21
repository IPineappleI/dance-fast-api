from datetime import datetime
from typing import Optional

from pydantic import BaseModel
import uuid


class DanceStyleBase(BaseModel):
    name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class DanceStyleInfo(DanceStyleBase):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class DanceStyleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
