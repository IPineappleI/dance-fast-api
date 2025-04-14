from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class LessonType(BaseModel):
    __tablename__ = "lesson_types"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, default=False, nullable=True)
    
    # Связи
    lessons = relationship("Lesson", back_populates="lesson_type")
    subscription_templates = relationship("SubscriptionLessonType", back_populates="lesson_type") 