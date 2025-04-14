from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    subscription_template_id = Column(UUID(as_uuid=True), ForeignKey("subscription_templates.id"), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)

    # Связи
    student = relationship("Student", back_populates="subscriptions")
    subscription_template = relationship("SubscriptionTemplate", back_populates="subscriptions")
    payment = relationship("Payment", back_populates="subscription")
    lessons = relationship("LessonSubscription", back_populates="subscription") 