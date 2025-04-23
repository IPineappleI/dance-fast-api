from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DanceStyle(BaseModel):
    __tablename__ = "dance_styles"

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    terminated = Column(Boolean, nullable=False, default=False)

    lesson_types = relationship("LessonType", uselist=True, back_populates="dance_style")
    #lessons = relationship("Lesson", back_populates="lesson_type")
    #subscription_templates = relationship("SubscriptionLessonType", back_populates="lesson_type")
    #teachers = relationship("TeacherLessonType", back_populates="lesson_type")
