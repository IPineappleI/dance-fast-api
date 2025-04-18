from pydantic import BaseModel


class GroupStudentBase(BaseModel):
    student: "StudentGroupInfo"

    class Config:
        from_attributes = True


class GroupTeacherBase(BaseModel):
    teacher: "TeacherGroupInfo"

    class Config:
        from_attributes = True


class MemberGroupBase(BaseModel):
    group: "GroupInfo"

    class Config:
        from_attributes = True


class TeacherLessonTypeBase(BaseModel):
    lesson_type: "LessonTypeInfo"

    class Config:
        from_attributes = True


class LessonTeacherBase(BaseModel):
    teacher: "TeacherLessonInfo"

    class Config:
        from_attributes = True


class LessonStudentBase(BaseModel):
    student: "StudentLessonInfo"

    class Config:
        from_attributes = True


class SubscriptionLessonTypeBase(BaseModel):
    lesson_type: "LessonTypeInfo"

    class Config:
        from_attributes = True


from app.schemas.student import StudentGroupInfo, StudentLessonInfo
from app.schemas.teacher import TeacherGroupInfo, TeacherLessonInfo
from app.schemas.group import GroupInfo
from app.schemas.lesson_type import LessonTypeInfo

GroupStudentBase.model_rebuild()
GroupTeacherBase.model_rebuild()
MemberGroupBase.model_rebuild()
TeacherLessonTypeBase.model_rebuild()
LessonTeacherBase.model_rebuild()
LessonStudentBase.model_rebuild()
SubscriptionLessonTypeBase.model_rebuild()
