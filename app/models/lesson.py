from datetime import datetime

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, select, exists, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database import TIMEZONE
from app.models.association import SubscriptionLessonType
from app.models.subscription_template import SubscriptionTemplate
from app.models.base import BaseModel


class Lesson(BaseModel):
    __tablename__ = 'lessons'

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    lesson_type_id = Column(UUID(as_uuid=True), ForeignKey('lesson_types.id'), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    finish_time = Column(DateTime(timezone=True), nullable=False)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey('classrooms.id'), nullable=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), nullable=True)
    is_confirmed = Column(Boolean, nullable=False)
    are_neighbours_allowed = Column(Boolean, nullable=False)
    terminated = Column(Boolean, nullable=False, default=False)

    classroom = relationship('Classroom', uselist=False, back_populates='lessons')
    lesson_type = relationship('LessonType', uselist=False, back_populates='lessons')
    group = relationship('Group', uselist=False, back_populates='lessons')

    teacher_lessons = relationship('TeacherLesson', uselist=True, back_populates='lesson')
    actual_teachers = relationship(
        'Teacher',
        primaryjoin='Lesson.id == TeacherLesson.lesson_id',
        secondary='teacher_lessons',
        secondaryjoin='TeacherLesson.teacher_id == Teacher.id',
        uselist=True,
        viewonly=True,
        overlaps='teacher_lessons',
        back_populates='lessons'
    )

    lesson_subscriptions = relationship('LessonSubscription', uselist=True, back_populates='lesson')
    subscriptions = relationship(
        'Subscription',
        primaryjoin='Lesson.id == LessonSubscription.lesson_id',
        secondary='lesson_subscriptions',
        secondaryjoin='LessonSubscription.subscription_id == Subscription.id',
        uselist=True,
        viewonly=True,
        overlaps='lesson_subscriptions',
        back_populates='lessons'
    )
    actual_students = relationship(
        'Student',
        primaryjoin='and_(Lesson.id == LessonSubscription.lesson_id, LessonSubscription.cancelled == False)',
        secondary='join(LessonSubscription, Subscription, '
                  'LessonSubscription.subscription_id == Subscription.id)',
        secondaryjoin='Subscription.student_id == Student.id',
        uselist=True,
        viewonly=True,
        overlaps='lesson_subscriptions, subscriptions',
        back_populates='lessons'
    )

    subscription_templates = relationship(
        'SubscriptionTemplate',
        primaryjoin='Lesson.lesson_type_id == SubscriptionLessonType.lesson_type_id',
        secondary='subscription_lesson_types',
        secondaryjoin='SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id',
        uselist=True,
        viewonly=True,
        back_populates='lessons'
    )

    @hybrid_property
    def fitting_subscription_templates(self):
        return [subscription_template for subscription_template in self.subscription_templates
                if not subscription_template.expiration_date
                or subscription_template.expiration_date > datetime.now(TIMEZONE)]

    @fitting_subscription_templates.expression
    def fitting_subscription_templates(cls):
        return select(SubscriptionTemplate).where(
            or_(
                SubscriptionTemplate.expiration_date == None,
                SubscriptionTemplate.expiration_date > datetime.now(TIMEZONE)
            ),
            exists(SubscriptionLessonType).where(
                SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id,
                SubscriptionLessonType.lesson_type_id == cls.lesson_type_id
            )
        )
