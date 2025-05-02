from pydantic import BaseModel

from app.schemas.subscription import SubscriptionFullInfo
from app.schemas.student import StudentMoreInfo
from app.schemas.teacher import TeacherMoreInfo
from app.schemas.subscriptionTemplate import SubscriptionTemplateFullInfo
from app.schemas.group import GroupFullInfo
from app.schemas.lessonType import LessonTypeFullInfo
from app.schemas.classroom import ClassroomInfo
import uuid
from typing import Optional, List
from datetime import datetime


class LessonCreate(BaseModel):
    name: str
    description: Optional[str] = None
    lesson_type_id: uuid.UUID
    start_time: datetime
    finish_time: datetime
    classroom_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None
    is_confirmed: bool
    are_neighbours_allowed: bool

    class Config:
        from_attributes = True


class LessonCreateIndividual(BaseModel):
    name: str
    description: Optional[str] = None
    lesson_type_id: uuid.UUID
    start_time: datetime
    finish_time: datetime
    classroom_id: uuid.UUID
    student_id: uuid.UUID
    are_neighbours_allowed: bool

    class Config:
        from_attributes = True


class LessonCreateGroup(BaseModel):
    name: str
    description: Optional[str] = None
    lesson_type_id: uuid.UUID
    start_time: datetime
    finish_time: datetime
    classroom_id: uuid.UUID
    group_id: uuid.UUID
    are_neighbours_allowed: bool

    class Config:
        from_attributes = True


class LessonCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    lesson_type_id: uuid.UUID
    start_time: datetime
    finish_time: datetime
    teacher_id: uuid.UUID
    are_neighbours_allowed: bool

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    is_confirmed: bool
    classroom_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class LessonInfo(LessonCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class LessonFullInfo(LessonInfo):
    lesson_type: LessonTypeFullInfo
    classroom: Optional[ClassroomInfo] = None
    subscription_templates: List[SubscriptionTemplateFullInfo]
    group: Optional[GroupFullInfo] = None
    actual_students: List[StudentMoreInfo]
    actual_teachers: List[TeacherMoreInfo]

    class Config:
        from_attributes = True


class LessonWithSubscriptions(LessonFullInfo):
    fitting_subscriptions: Optional[List[SubscriptionFullInfo]] = None
    used_subscription: Optional[SubscriptionFullInfo] = None

    class Config:
        from_attributes = True


class LessonPage(BaseModel):
    lessons: List[LessonInfo]
    total: int

    class Config:
        from_attributes = True


class LessonFullInfoPage(BaseModel):
    lessons: List[LessonFullInfo]
    total: int

    class Config:
        from_attributes = True


class LessonFilters(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_confirmed: Optional[bool] = None
    are_neighbours_allowed: Optional[bool] = None
    is_group: Optional[bool] = None
    terminated: Optional[bool] = None

    teacher_ids: Optional[List[uuid.UUID]] = None
    student_ids: Optional[List[uuid.UUID]] = None
    classroom_ids: Optional[List[uuid.UUID]] = None
    dance_style_ids: Optional[List[uuid.UUID]] = None
    lesson_type_ids: Optional[List[uuid.UUID]] = None
    subscription_template_ids: Optional[List[uuid.UUID]] = None
    level_ids: Optional[List[uuid.UUID]] = None
    group_ids: Optional[List[uuid.UUID]] = None

    class Config:
        from_attributes = True


class LessonFiltersGroup(LessonFilters):
    is_participant: Optional[bool] = None

    class Config:
        from_attributes = True


class LessonUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    lesson_type_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    classroom_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None
    is_confirmed: Optional[bool] = None
    are_neighbours_allowed: Optional[bool] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
