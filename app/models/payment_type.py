from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PaymentType(BaseModel):
    __tablename__ = "payment_types"

    name = Column(String, nullable=False, unique=True)
    terminated = Column(Boolean, nullable=False, default=False)

    payments = relationship("Payment", back_populates="payment_type")
