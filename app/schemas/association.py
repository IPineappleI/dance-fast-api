from pydantic import BaseModel


class StudentForLists(BaseModel):
    student: "StudentMoreInfo"

    class Config:
        from_attributes = True


class TeacherForLists(BaseModel):
    teacher: "TeacherMoreInfo"

    class Config:
        from_attributes = True


class GroupForLists(BaseModel):
    group: "GroupMoreInfo"

    class Config:
        from_attributes = True


class LessonTypeForLists(BaseModel):
    lesson_type: "LessonTypeFullInfo"

    class Config:
        from_attributes = True


from app.schemas.student import StudentMoreInfo
from app.schemas.teacher import TeacherMoreInfo
from app.schemas.group import GroupMoreInfo
from app.schemas.lessonType import LessonTypeFullInfo

StudentForLists.model_rebuild()
TeacherForLists.model_rebuild()
GroupForLists.model_rebuild()
LessonTypeForLists.model_rebuild()
