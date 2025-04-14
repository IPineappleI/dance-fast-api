from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

# Устанавливаем параметры подключения напрямую
user = os.getenv("PGUSER")
password = os.getenv("PGPASSWORD")
host = os.getenv("PGHOST")
port = os.getenv("PGPORT")
database = os.getenv("DATABASE_NAME")

# Принудительно устанавливаем правильный URL соединения
DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{database}"
DATABASE_NAME = "railway"

print(f"Используемый DATABASE_URL: {DATABASE_URL}")

print(f"Используемые параметры: user={user}, host={host}, port={port}, database={database}")

# def init_db():
#     # Подключаемся к postgres для создания базы данных
#     try:
#         conn = psycopg2.connect(
#             dbname='railway',
#             user=user,
#             password=password,
#             host=host,
#             port=port
#         )
#         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#
#         with conn.cursor() as cur:
#             # Проверяем существование базы данных
#             cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE_NAME,))
#             exists = cur.fetchone()
#
#             if not exists:
#                 # Создаем базу данных
#                 cur.execute(f"CREATE DATABASE {DATABASE_NAME}")
#                 print(f"База данных {DATABASE_NAME} успешно создана")
#             else:
#                 print(f"База данных {DATABASE_NAME} уже существует")
#
#     except Exception as e:
#         print(f"Ошибка при инициализации базы данных: {e}")
#     finally:
#         if 'conn' in locals() and conn:
#             conn.close()
#
#     # Создаем движок для работы с SQLAlchemy
#     try:
#         test_engine = create_engine(DATABASE_URL)
#         with test_engine.connect() as conn:
#             print("Тестовое подключение к базе данных успешно")
#     except Exception as e:
#         print(f"Ошибка при тестовом подключении: {e}")

# Создаем движок для работы с нашей базой данных
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
