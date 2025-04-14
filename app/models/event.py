from sqlalchemy import Column, ForeignKey, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Event(BaseModel):
    __tablename__ = "events"

    event_type_id = Column(UUID(as_uuid=True), ForeignKey("event_types.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    photo_url = Column(String, nullable=False)
    terminated = Column(Boolean, default=False, nullable=True)

    # Связи
    event_type = relationship("EventType", back_populates="events") 