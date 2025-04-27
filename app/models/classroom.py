from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Classroom(BaseModel):
    __tablename__ = 'classrooms'

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, nullable=False, default=False)

    lessons = relationship('Lesson', uselist=True, back_populates='classroom')
