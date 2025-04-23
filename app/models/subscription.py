from sqlalchemy import Column, ForeignKey, DateTime, func, select, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.models.subscription_template import SubscriptionTemplate
from app.models.base import BaseModel
from app.models import LessonSubscription


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    subscription_template_id = Column(UUID(as_uuid=True), ForeignKey("subscription_templates.id"), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)

    subscription_template = relationship("SubscriptionTemplate", uselist=False, back_populates="subscriptions")
    student = relationship("Student", uselist=False, back_populates="subscriptions")
    payment = relationship("Payment", uselist=False, back_populates="subscription")

    lesson_subscriptions = relationship("LessonSubscription", uselist=True, back_populates="subscription")
    active_lesson_subscriptions = relationship(
        "LessonSubscription",
        primaryjoin="and_(LessonSubscription.subscription_id == Subscription.id, "
                    "LessonSubscription.cancelled == False)",
        uselist=True,
        viewonly=True,
        overlaps="lesson_subscriptions"
    )
    lessons = relationship(
        "Lesson",
        primaryjoin="Subscription.id == LessonSubscription.subscription_id",
        secondary="lesson_subscriptions",
        secondaryjoin="LessonSubscription.lesson_id == Lesson.id",
        uselist=True,
        viewonly=True,
        overlaps="lesson_subscriptions, active_lesson_subscriptions",
        back_populates="subscriptions"
    )

    @hybrid_property
    def lessons_left(self):
        return self.subscription_template.lesson_count - len(self.active_lesson_subscriptions)

    @lessons_left.expression
    def lessons_left(cls):
        return SubscriptionTemplate.lesson_count - (select(
            func.count(LessonSubscription.lesson_id)
        ).where(and_(
                LessonSubscription.subscription_id == cls.id,
                LessonSubscription.cancelled == False
            )).scalar_subquery()
        )
