from sqlalchemy import Column, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Slot(BaseModel):
    __tablename__ = 'slots'

    teacher_id = Column(UUID(as_uuid=True), ForeignKey('teachers.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time(timezone=True), nullable=False)
    end_time = Column(Time(timezone=True), nullable=False)

    teacher = relationship('Teacher', uselist=False, back_populates='slots')
