from pydantic import BaseModel


class GroupStudentBase(BaseModel):
    student: "StudentInfo"

    class Config:
        from_attributes = True


class GroupTeacherBase(BaseModel):
    teacher: "TeacherInfo"

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
    teacher: "TeacherInfo"

    class Config:
        from_attributes = True


class LessonStudentBase(BaseModel):
    student: "StudentInfo"

    class Config:
        from_attributes = True


class SubscriptionLessonTypeBase(BaseModel):
    lesson_type: "LessonTypeInfo"

    class Config:
        from_attributes = True


from app.schemas.student import StudentInfo
from app.schemas.teacher import TeacherInfo
from app.schemas.group import GroupInfo
from app.schemas.lesson_type import LessonTypeInfo

GroupStudentBase.model_rebuild()
GroupTeacherBase.model_rebuild()
MemberGroupBase.model_rebuild()
TeacherLessonTypeBase.model_rebuild()
LessonTeacherBase.model_rebuild()
LessonStudentBase.model_rebuild()
SubscriptionLessonTypeBase.model_rebuild()
