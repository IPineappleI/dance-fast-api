from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class EventType(BaseModel):
    __tablename__ = 'event_types'

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    terminated = Column(Boolean, nullable=False, default=False)

    events = relationship('Event', uselist=True, back_populates='event_type')
