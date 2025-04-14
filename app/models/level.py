from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Level(BaseModel):
    __tablename__ = "levels"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, default=False, nullable=True)

    # Связи
    students = relationship("Student", back_populates="level")
    groups = relationship("Group", back_populates="level")
