from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

import uuid

from app.schemas.subscription import SubscriptionMoreInfo
from app.schemas.paymentType import PaymentTypeInfo


class PaymentCreate(BaseModel):
    payment_type_id: uuid.UUID
    details: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentInfo(PaymentCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class PaymentFullInfo(PaymentInfo):
    payment_type: PaymentTypeInfo
    subscription: SubscriptionMoreInfo

    class Config:
        from_attributes = True


class PaymentPage(BaseModel):
    payments: List[PaymentInfo]
    total: int

    class Config:
        from_attributes = True


class PaymentFullInfoPage(BaseModel):
    payments: List[PaymentFullInfo]
    total: int

    class Config:
        from_attributes = True


class PaymentFilters(BaseModel):
    payment_type_ids: Optional[List[uuid.UUID]] = None
    student_id: Optional[uuid.UUID] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    payment_type_id: Optional[uuid.UUID] = None
    details: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
