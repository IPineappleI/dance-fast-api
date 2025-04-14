from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PaymentType(BaseModel):
    __tablename__ = "payment_types"

    name = Column(String, nullable=False)

    # Связи
    payments = relationship("Payment", back_populates="payment_type") 