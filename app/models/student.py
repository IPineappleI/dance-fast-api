from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Student(BaseModel):
    __tablename__ = 'students'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    level_id = Column(UUID(as_uuid=True), ForeignKey('levels.id'), nullable=False)

    user = relationship('User', uselist=False, back_populates='student')
    level = relationship('Level', uselist=False, back_populates='students')

    student_groups = relationship('StudentGroup', uselist=True, back_populates='student')
    groups = relationship(
        'Group',
        primaryjoin='Student.id == StudentGroup.student_id',
        secondary='student_groups',
        secondaryjoin='StudentGroup.group_id == Group.id',
        uselist=True,
        viewonly=True,
        overlaps='student_groups',
        back_populates='students'
    )

    subscriptions = relationship('Subscription', uselist=True, back_populates='student')
    lessons = relationship(
        'Lesson',
        primaryjoin='Student.id == Subscription.student_id',
        secondary='join(Subscription, LessonSubscription, '
                  'Subscription.id == LessonSubscription.subscription_id)',
        secondaryjoin='LessonSubscription.lesson_id == Lesson.id',
        uselist=True,
        viewonly=True,
        overlaps='subscriptions',
        back_populates='actual_students'
    )
