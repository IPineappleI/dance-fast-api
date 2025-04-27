from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
import uuid


class PaymentTypeCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True


class PaymentTypeInfo(PaymentTypeCreate):
    id: uuid.UUID
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class PaymentTypePage(BaseModel):
    payment_types: List[PaymentTypeInfo]
    total: int

    class Config:
        from_attributes = True


class PaymentTypeFilters(BaseModel):
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class PaymentTypeUpdate(BaseModel):
    name: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
