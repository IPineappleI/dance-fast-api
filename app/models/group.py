from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Group(BaseModel):
    __tablename__ = 'groups'

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    level_id = Column(UUID(as_uuid=True), ForeignKey('levels.id'), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    terminated = Column(Boolean, nullable=False, default=False)

    level = relationship('Level', uselist=False, back_populates='groups')
    lessons = relationship('Lesson', uselist=True, back_populates='group')

    teacher_groups = relationship('TeacherGroup', uselist=True, back_populates='group')
    teachers = relationship(
        'Teacher',
        primaryjoin='Group.id == TeacherGroup.group_id',
        secondary='teacher_groups',
        secondaryjoin='TeacherGroup.teacher_id == Teacher.id',
        uselist=True,
        viewonly=True,
        overlaps='teacher_groups',
        back_populates='groups'
    )

    student_groups = relationship('StudentGroup', uselist=True, back_populates='group')
    students = relationship(
        'Student',
        primaryjoin='Group.id == StudentGroup.group_id',
        secondary='student_groups',
        secondaryjoin='StudentGroup.student_id == Student.id',
        uselist=True,
        viewonly=True,
        overlaps='student_groups',
        back_populates='groups'
    )
