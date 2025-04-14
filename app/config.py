import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional

# Загрузка переменных окружения из файла .env
load_dotenv()

class Settings(BaseSettings):
    # Настройки базы данных
    DATABASE_URL: str
    DATABASE_NAME: str
    # Настройки приложения
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    
    # Настройки сервера
    HOST: str
    PORT: int
    
    # Настройки JWT авторизации
    SECRET_KEY: Optional[str] = "0192u9041720917409104"
    ALGORITHM: Optional[str] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = 60

    @field_validator('DATABASE_URL')
    def validate_database_url(cls, v):
        if not v.startswith('postgresql://'):
            raise ValueError('DATABASE_URL должен начинаться с postgresql://')
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Создание экземпляра настроек
settings = Settings() 