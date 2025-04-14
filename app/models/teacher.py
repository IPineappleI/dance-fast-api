from sqlalchemy import Column, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Teacher(BaseModel):
    __tablename__ = "teachers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    terminated = Column(Boolean, default=False, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="teacher")
    slots = relationship("Slot", back_populates="teacher")
    lessons = relationship("TeacherLesson", back_populates="teacher")
    groups = relationship("TeacherGroup", back_populates="teacher") 