from sqlalchemy import Column, Integer, DateTime, Numeric, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class SubscriptionTemplate(BaseModel):
    __tablename__ = "subscription_templates"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    lesson_count = Column(Integer, nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    expiration_day_count = Column(Integer, nullable=True)
    price = Column(Numeric(8, 2), nullable=False)
    active = Column(Boolean, default=True)

    # Связи
    subscriptions = relationship("Subscription", back_populates="subscription_template")
    lesson_types = relationship("SubscriptionLessonType", back_populates="subscription_template") 