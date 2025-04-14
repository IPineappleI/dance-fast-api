from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class EventType(BaseModel):
    __tablename__ = "event_types"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, default=False, nullable=True)

    # Связи
    events = relationship("Event", back_populates="event_type")
