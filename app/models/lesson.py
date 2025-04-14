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
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    is_confirmed = Column(Boolean, default=False)
    are_neighbours_allowed = Column(Boolean, default=False)
    terminated = Column(Boolean, default=False, nullable=True)
    
    # Связи
    lesson_type = relationship("LessonType", back_populates="lessons")
    classroom = relationship("Classroom", back_populates="lessons")
    group = relationship("Group", back_populates="lessons")
    teachers = relationship("TeacherLesson", back_populates="lesson")
    subscriptions = relationship("LessonSubscription", back_populates="lesson") 