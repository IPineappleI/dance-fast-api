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
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    is_confirmed = Column(Boolean, nullable=False)
    are_neighbours_allowed = Column(Boolean, nullable=False)
    terminated = Column(Boolean, nullable=False, default=False)

    classroom = relationship("Classroom", uselist=False, back_populates="lessons")
    lesson_type = relationship("LessonType", uselist=False, back_populates="lessons")
    group = relationship("Group", uselist=False, back_populates="lessons")

    teacher_lessons = relationship("TeacherLesson", uselist=True, back_populates="lesson")
    actual_teachers = relationship(
        "Teacher",
        primaryjoin="Lesson.id == TeacherLesson.lesson_id",
        secondary="teacher_lessons",
        secondaryjoin="TeacherLesson.teacher_id == Teacher.id",
        uselist=True,
        viewonly=True,
        overlaps="teacher_lessons",
        back_populates="lessons"
    )

    lesson_subscriptions = relationship("LessonSubscription", uselist=True, back_populates="lesson")
    subscriptions = relationship(
        "Subscription",
        primaryjoin="Lesson.id == LessonSubscription.lesson_id",
        secondary="lesson_subscriptions",
        secondaryjoin="LessonSubscription.subscription_id == Subscription.id",
        uselist=True,
        viewonly=True,
        overlaps="lesson_subscriptions",
        back_populates="lessons"
    )
    actual_students = relationship(
        "Student",
        primaryjoin="Lesson.id == LessonSubscription.lesson_id",
        secondary="join(LessonSubscription, Subscription, "
                  "LessonSubscription.subscription_id == Subscription.id)",
        secondaryjoin="Subscription.student_id == Student.id",
        uselist=True,
        viewonly=True,
        overlaps="lesson_subscriptions, subscriptions",
        back_populates="lessons"
    )

    subscription_templates = relationship(
        "SubscriptionTemplate",
        primaryjoin="Lesson.lesson_type_id == SubscriptionLessonType.lesson_type_id",
        secondary="subscription_lesson_types",
        secondaryjoin="SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id",
        uselist=True,
        viewonly=True,
        back_populates="lessons"
    )
