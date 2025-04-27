from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import *


class TeacherGroup(Base):
    __tablename__ = 'teacher_groups'

    teacher_id = Column(UUID(as_uuid=True), ForeignKey('teachers.id'), primary_key=True, nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), primary_key=True, nullable=False)

    teacher = relationship('Teacher', uselist=False, back_populates='teacher_groups')
    group = relationship('Group', uselist=False, back_populates='teacher_groups')


class StudentGroup(Base):
    __tablename__ = 'student_groups'

    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'), primary_key=True, nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), primary_key=True, nullable=False)

    student = relationship('Student', uselist=False, back_populates='student_groups')
    group = relationship('Group', uselist=False, back_populates='student_groups')


class TeacherLessonType(Base):
    __tablename__ = 'teacher_lesson_types'

    teacher_id = Column(UUID(as_uuid=True), ForeignKey('teachers.id'), primary_key=True, nullable=False)
    lesson_type_id = Column(UUID(as_uuid=True), ForeignKey('lesson_types.id'), primary_key=True, nullable=False)

    teacher = relationship('Teacher', uselist=False, back_populates='teacher_lesson_types')
    lesson_type = relationship('LessonType', uselist=False, back_populates='teacher_lesson_types')


class TeacherLesson(Base):
    __tablename__ = 'teacher_lessons'

    teacher_id = Column(UUID(as_uuid=True), ForeignKey('teachers.id'), primary_key=True, nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey('lessons.id'), primary_key=True, nullable=False)

    teacher = relationship('Teacher', uselist=False, back_populates='teacher_lessons')
    lesson = relationship('Lesson', uselist=False, back_populates='teacher_lessons')


class SubscriptionLessonType(Base):
    __tablename__ = 'subscription_lesson_types'

    subscription_template_id = Column(UUID(as_uuid=True), ForeignKey('subscription_templates.id'), primary_key=True,
                                      nullable=False)
    lesson_type_id = Column(UUID(as_uuid=True), ForeignKey('lesson_types.id'), primary_key=True, nullable=False)

    subscription_template = relationship('SubscriptionTemplate', uselist=False,
                                         back_populates='subscription_lesson_types')
    lesson_type = relationship('LessonType', uselist=False, back_populates='subscription_lesson_types')


class LessonSubscription(BaseModel):
    __tablename__ = 'lesson_subscriptions'

    lesson_id = Column(UUID(as_uuid=True), ForeignKey('lessons.id'), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    cancelled = Column(Boolean, nullable=False, default=False)

    lesson = relationship('Lesson', uselist=False, back_populates='lesson_subscriptions')
    subscription = relationship('Subscription', uselist=False, back_populates='lesson_subscriptions')
