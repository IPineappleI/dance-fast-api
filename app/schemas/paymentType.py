from typing import Optional

from pydantic import BaseModel
import uuid


class PaymentTypeBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class PaymentTypeInfo(PaymentTypeBase):
    id: uuid.UUID
    terminated: bool

    class Config:
        from_attributes = True


class PaymentTypeUpdate(BaseModel):
    name: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
