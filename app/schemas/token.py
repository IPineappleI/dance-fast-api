from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Схема для токена доступа."""
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Схема для данных токена."""
    id: Optional[str] = None

    class Config:
        from_attributes = True
