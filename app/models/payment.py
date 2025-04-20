from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Payment(BaseModel):
    __tablename__ = "payments"

    payment_type_id = Column(UUID(as_uuid=True), ForeignKey("payment_types.id"), nullable=False)
    details = Column(String, nullable=True)
    terminated = Column(Boolean, nullable=False, default=False)

    payment_type = relationship("PaymentType", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payment")
