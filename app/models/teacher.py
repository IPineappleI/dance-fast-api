from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Teacher(BaseModel):
    __tablename__ = 'teachers'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)

    user = relationship('User', uselist=False, back_populates='teacher')
    slots = relationship('Slot', uselist=True, back_populates='teacher')

    teacher_lessons = relationship('TeacherLesson', uselist=True, back_populates='teacher')
    lessons = relationship(
        'Lesson',
        primaryjoin='Teacher.id == TeacherLesson.teacher_id',
        secondary='teacher_lessons',
        secondaryjoin='TeacherLesson.lesson_id == Lesson.id',
        uselist=True,
        viewonly=True,
        overlaps='teacher_lessons',
        back_populates='actual_teachers'
    )

    teacher_groups = relationship('TeacherGroup', uselist=True, back_populates='teacher')
    groups = relationship(
        'Group',
        primaryjoin='Teacher.id == TeacherGroup.teacher_id',
        secondary='teacher_groups',
        secondaryjoin='TeacherGroup.group_id == Group.id',
        uselist=True,
        viewonly=True,
        overlaps='teacher_groups',
        back_populates='teachers'
    )

    teacher_lesson_types = relationship('TeacherLessonType', uselist=True, back_populates='teacher')
    lesson_types = relationship(
        'LessonType',
        primaryjoin='Teacher.id == TeacherLessonType.teacher_id',
        secondary='teacher_lesson_types',
        secondaryjoin='TeacherLessonType.lesson_type_id == LessonType.id',
        uselist=True,
        viewonly=True,
        overlaps='teacher_lesson_types',
        back_populates='teachers'
    )
