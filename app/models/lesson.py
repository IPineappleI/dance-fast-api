from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Lesson(BaseModel):
    __tablename__ = "lessons"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    lesson_type_id = Column(UUID(as_uuid=True), ForeignKey("lesson_types.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    finish_time = Column(DateTime(timezone=True), nullable=False)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    is_confirmed = Column(Boolean, nullable=False)
    are_neighbours_allowed = Column(Boolean, nullable=False)
    terminated = Column(Boolean, nullable=False, default=False)

    lesson_type = relationship("LessonType", back_populates="lessons")
    classroom = relationship("Classroom", back_populates="lessons")
    group = relationship("Group", back_populates="lessons")
    actual_teachers = relationship("TeacherLesson", back_populates="lesson")
    subscriptions = relationship("LessonSubscription", back_populates="lesson")
    actual_students = relationship(
        "Student",
        primaryjoin="Lesson.id == LessonSubscription.lesson_id",
        secondary="join(LessonSubscription, Subscription, "
                  "LessonSubscription.subscription_id == Subscription.id)",
        secondaryjoin="Subscription.student_id == Student.id",
        viewonly=True,
        overlaps="subscriptions",
        back_populates="lessons"
    )
    subscription_templates = relationship(
        "SubscriptionTemplate",
        primaryjoin="Lesson.lesson_type_id == SubscriptionLessonType.lesson_type_id",
        secondary="subscription_lesson_types",
        secondaryjoin="SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id",
        viewonly=True,
        back_populates="lessons")
