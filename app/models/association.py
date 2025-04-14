from sqlalchemy import Column, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class TeacherLesson(Base):
    __tablename__ = "teacher_lessons"

    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), primary_key=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), primary_key=True)

    # Связи
    teacher = relationship("Teacher", back_populates="lessons")
    lesson = relationship("Lesson", back_populates="teachers")


class TeacherGroup(Base):
    __tablename__ = "teacher_groups"

    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)

    # Связи
    teacher = relationship("Teacher", back_populates="groups")
    group = relationship("Group", back_populates="teachers")


class StudentGroup(Base):
    __tablename__ = "student_groups"

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    join_date = Column(DateTime(timezone=True), nullable=True)

    # Связи
    student = relationship("Student", back_populates="groups")
    group = relationship("Group", back_populates="students")


class LessonSubscription(Base):
    __tablename__ = "lesson_subscriptions"

    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), primary_key=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), primary_key=True)
    cancelled = Column(Boolean, default=False)

    # Связи
    subscription = relationship("Subscription", back_populates="lessons")
    lesson = relationship("Lesson", back_populates="subscriptions")


class SubscriptionLessonType(Base):
    __tablename__ = "subscription_lesson_types"

    subscription_template_id = Column(UUID(as_uuid=True), ForeignKey("subscription_templates.id"), primary_key=True)
    lesson_type_id = Column(UUID(as_uuid=True), ForeignKey("lesson_types.id"), primary_key=True)

    # Связи
    subscription_template = relationship("SubscriptionTemplate", back_populates="lesson_types")
    lesson_type = relationship("LessonType", back_populates="subscription_templates") 