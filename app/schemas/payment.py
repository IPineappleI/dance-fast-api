from typing import Optional

from pydantic import BaseModel
from app.schemas.paymentType import PaymentTypeInfo
import uuid


class PaymentBase(BaseModel):
    """Базовая схема платежа."""
    payment_type_id: uuid.UUID
    details: str | None = None

    class Config:
        from_attributes = True


class PaymentInfo(PaymentBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    payment_type_id: Optional[uuid.UUID] = None
    details: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentInfoWithType(PaymentInfo):
    payment_type: PaymentTypeInfo

    class Config:
        from_attributes = True
