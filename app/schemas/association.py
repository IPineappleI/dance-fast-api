from pydantic import BaseModel


class AssociationStudent(BaseModel):
    student: "StudentMoreInfo"

    class Config:
        from_attributes = True


class AssociationTeacher(BaseModel):
    teacher: "TeacherMoreInfo"

    class Config:
        from_attributes = True


class AssociationGroup(BaseModel):
    group: "GroupMoreInfo"

    class Config:
        from_attributes = True


class AssociationLessonType(BaseModel):
    lesson_type: "LessonTypeFullInfo"

    class Config:
        from_attributes = True


from app.schemas.student import StudentMoreInfo
from app.schemas.teacher import TeacherMoreInfo
from app.schemas.group import GroupMoreInfo
from app.schemas.lessonType import LessonTypeFullInfo

AssociationStudent.model_rebuild()
AssociationTeacher.model_rebuild()
AssociationGroup.model_rebuild()
AssociationLessonType.model_rebuild()
