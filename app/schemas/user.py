from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import uuid


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: str

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: str
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Схема для создания пользователя."""
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: str
    password: str

    @validator('password')
    def password_strength(cls, v):
        """Проверяет сложность пароля."""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для входа пользователя."""
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
