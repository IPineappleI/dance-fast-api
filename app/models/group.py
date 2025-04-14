from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Group(BaseModel):
    __tablename__ = "groups"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id"), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    terminated = Column(Boolean, default=False, nullable=True)

    # Связи
    level = relationship("Level", back_populates="groups")
    students = relationship("StudentGroup", back_populates="group")
    teachers = relationship("TeacherGroup", back_populates="group")
    lessons = relationship("Lesson", back_populates="group") 