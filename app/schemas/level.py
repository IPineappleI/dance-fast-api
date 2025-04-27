from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
import uuid


class LevelCreate(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class LevelInfo(LevelCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class LevelPage(BaseModel):
    levels: List[LevelInfo]
    total: int

    class Config:
        from_attributes = True


class LevelFilters(BaseModel):
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class LevelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
