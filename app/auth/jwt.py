from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.admin import Admin
from app.schemas.token import TokenData

# Константы
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Схема OAuth2 для получения токена через форму логина
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT токен доступа."""
    to_encode = data.copy()
    
    # Устанавливаем время истечения срока действия токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Создаем JWT токен
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """Проверяет JWT токен и возвращает данные пользователя."""
    try:
        # Декодируем JWT токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        # Создаем объект с данными пользователя
        token_data = TokenData(id=user_id)
        return token_data
    
    except JWTError:
        raise credentials_exception

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получает текущего пользователя по токену."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Проверяем токен и получаем данные пользователя
    token_data = verify_token(token, credentials_exception)
    
    # Получаем пользователя из базы данных
    user = db.query(User).filter(User.id == token_data.id).first()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Admin:
    """Проверяет, что текущий пользователь является администратором."""
    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return admin

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверяет, что текущий пользователь активен."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неактивный аккаунт",
        )
    return current_user 