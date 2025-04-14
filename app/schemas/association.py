from pydantic import BaseModel
from datetime import datetime


class GroupStudentBase(BaseModel):
    student: "StudentGroupInfo"
    join_date: datetime

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


from app.schemas.group import GroupInfo
from app.schemas.student import StudentGroupInfo
from app.schemas.teacher import TeacherGroupInfo

GroupStudentBase.model_rebuild()
GroupTeacherBase.model_rebuild()
MemberGroupBase.model_rebuild()
