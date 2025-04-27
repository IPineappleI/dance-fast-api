from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Level(BaseModel):
    __tablename__ = 'levels'

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, nullable=False, default=False)

    groups = relationship('Group', uselist=True, back_populates='level')
    students = relationship('Student', uselist=True, back_populates='level')
