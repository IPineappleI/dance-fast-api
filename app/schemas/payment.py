from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.schemas.paymentType import PaymentTypeInfo
import uuid


class PaymentBase(BaseModel):
    payment_type_id: uuid.UUID
    details: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentInfo(PaymentBase):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class PaymentFullInfo(PaymentInfo):
    payment_type: PaymentTypeInfo

    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    payment_type_id: Optional[uuid.UUID] = None
    details: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
