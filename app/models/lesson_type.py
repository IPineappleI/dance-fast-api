from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class LessonType(BaseModel):
    __tablename__ = "lesson_types"

    dance_style_id = Column(UUID(as_uuid=True), ForeignKey("dance_styles.id"), nullable=False)
    is_group = Column(Boolean, nullable=False)
    terminated = Column(Boolean, nullable=False, default=False)

    dance_style = relationship("DanceStyle", uselist=False, back_populates="lesson_types")
    lessons = relationship("Lesson", uselist=True, back_populates="lesson_type")

    teacher_lesson_types = relationship("TeacherLessonType", uselist=True, back_populates="lesson_type")
    teachers = relationship(
        "Teacher",
        primaryjoin="LessonType.id == TeacherLessonType.lesson_type_id",
        secondary="teacher_lesson_types",
        secondaryjoin="TeacherLessonType.teacher_id == Teacher.id",
        uselist=True,
        viewonly=True,
        overlaps="teacher_lesson_types",
        back_populates="lesson_types"
    )

    subscription_lesson_types = relationship("SubscriptionLessonType", uselist=True, back_populates="lesson_type")
    subscription_templates = relationship(
        "SubscriptionTemplate",
        primaryjoin="LessonType.id == SubscriptionLessonType.lesson_type_id",
        secondary="subscription_lesson_types",
        secondaryjoin="SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id",
        uselist=True,
        viewonly=True,
        overlaps="subscription_lesson_types",
        back_populates="lesson_types"
    )
