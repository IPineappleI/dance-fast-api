from datetime import datetime

from pydantic import BaseModel

from app.schemas.subscription import SubscriptionFullInfo
from app.schemas.level import LevelInfo
import uuid
from typing import Optional, List


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    level_id: uuid.UUID
    max_capacity: int

    class Config:
        from_attributes = True


class GroupInfo(GroupCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class GroupMoreInfo(GroupInfo):
    level: LevelInfo

    class Config:
        from_attributes = True


class GroupFullInfo(GroupMoreInfo):
    students: List['StudentMoreInfo']
    teachers: List['TeacherMoreInfo']

    class Config:
        from_attributes = True


class GroupWithSubscriptions(GroupFullInfo):
    fitting_subscriptions: Optional[List[SubscriptionFullInfo]] = None

    class Config:
        from_attributes = True


class GroupPage(BaseModel):
    groups: List[GroupInfo]
    total: int

    class Config:
        from_attributes = True


class GroupFullInfoPage(BaseModel):
    groups: List[GroupFullInfo]
    total: int

    class Config:
        from_attributes = True


class GroupFilters(BaseModel):
    has_teachers: Optional[bool] = None
    has_students: Optional[bool] = None
    terminated: Optional[bool] = None

    teacher_ids: Optional[List[uuid.UUID]] = None
    student_ids: Optional[List[uuid.UUID]] = None
    dance_style_ids: Optional[List[uuid.UUID]] = None
    level_ids: Optional[List[uuid.UUID]] = None

    class Config:
        from_attributes = True


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level_id: Optional[uuid.UUID] = None
    max_capacity: Optional[int] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


from app.schemas.student import StudentMoreInfo
from app.schemas.teacher import TeacherMoreInfo

GroupFullInfo.model_rebuild()
