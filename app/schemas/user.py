from datetime import datetime
from email_validator import validate_email
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import uuid


class UserInfo(BaseModel):
    id: uuid.UUID
    email: EmailStr
    email_confirmed: bool
    receive_email: bool
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: str
    created_at: datetime
    terminated: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    receive_email: Optional[bool] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: str
    password: str

    @field_validator('email')
    def validate_email(cls, email):
        return validate_email(email).normalized

    @field_validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return password

    class Config:
        from_attributes = True


class UserFilters(BaseModel):
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    receive_email: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    terminated: Optional[bool] = None

    class Config:
        from_attributes = True
