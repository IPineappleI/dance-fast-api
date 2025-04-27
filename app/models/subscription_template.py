from sqlalchemy import Column, Integer, DateTime, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SubscriptionTemplate(BaseModel):
    __tablename__ = 'subscription_templates'

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    lesson_count = Column(Integer, nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    expiration_day_count = Column(Integer, nullable=True)
    price = Column(Numeric(8, 2), nullable=False)

    subscriptions = relationship('Subscription', uselist=True, back_populates='subscription_template')

    subscription_lesson_types = relationship('SubscriptionLessonType', uselist=True, back_populates='subscription_template')
    lesson_types = relationship(
        'LessonType',
        primaryjoin='SubscriptionTemplate.id == SubscriptionLessonType.subscription_template_id',
        secondary='subscription_lesson_types',
        secondaryjoin='SubscriptionLessonType.lesson_type_id == LessonType.id',
        uselist=True,
        viewonly=True,
        overlaps='subscription_lesson_types',
        back_populates='subscription_templates'
    )
    lessons = relationship(
        'Lesson',
        primaryjoin='SubscriptionTemplate.id == SubscriptionLessonType.subscription_template_id',
        secondary='subscription_lesson_types',
        secondaryjoin='SubscriptionLessonType.lesson_type_id == Lesson.lesson_type_id',
        uselist=True,
        viewonly=True,
        overlaps='subscription_lesson_types, lesson_types',
        back_populates='subscription_templates'
    )
