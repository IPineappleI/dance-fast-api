from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Classroom(BaseModel):
    __tablename__ = "classrooms"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, default=False, nullable=True)
    # Связи
    lessons = relationship("Lesson", back_populates="classroom")
