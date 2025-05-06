from pytz import timezone
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = 'postgresql://postgres:postgrya@localhost:5432/dance_api'
DATABASE_NAME = 'dance_api'

print(f'Используемый DATABASE_URL: {DATABASE_URL}')

user = 'postgres'
password = 'postgrya'
host = 'localhost'
port = '5432'
database = 'dance-api'

print(f'Используемые параметры: user={user}, host={host}, port={port}, database={database}')

TIMEZONE_NAME = 'Europe/Moscow'
TIMEZONE = timezone(TIMEZONE_NAME)


def init_db():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cur:
            cur.execute(f'SELECT 1 FROM pg_database WHERE datname = %s', (DATABASE_NAME,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(f'CREATE DATABASE {DATABASE_NAME}')
                print(f'База данных {DATABASE_NAME} успешно создана')
                cur.execute(f"SET TIMEZONE = '{TIMEZONE_NAME}'")
                print(f'Выставлен часовой пояс {TIMEZONE_NAME}')
            else:
                print(f'База данных {DATABASE_NAME} уже существует')

    except Exception as e:
        print(f'Ошибка при инициализации базы данных: {e}')
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    try:
        test_engine = create_engine(DATABASE_URL)
        with test_engine.connect() as conn:
            print('Тестовое подключение к базе данных успешно')
    except Exception as e:
        print(f'Ошибка при тестовом подключении: {e}')


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
