from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base, init_db
# Явно импортируем все модели
from app.routers import users, auth, events, eventTypes, classrooms, subscription_templates, paymentTypes, payments, \
    subscription, slots, students, levels, teachers, lessonTypes, groups, admins, lessons
import os

print("Запуск приложения...")
print(f"DATABASE_URL в окружении: {os.getenv('DATABASE_URL')}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск события startup")
    try:
        # Создаем базу данных, если её нет
        init_db()

        # Создаем все таблицы
        # Base.metadata создаёт все таблицы из моделей, которые наследуются от Base
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
    yield
    print("Завершение работы приложения")


app = FastAPI(
    title="Dance Studio API",
    description="API для мобильного приложения школы танцев",
    version="0.1.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(users.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(groups.router)
app.include_router(levels.router)
app.include_router(events.router)
app.include_router(eventTypes.router)
app.include_router(lessons.router)
app.include_router(lessonTypes.router)
app.include_router(classrooms.router)
app.include_router(subscription.router)
app.include_router(subscription_templates.router)
app.include_router(payments.router)
app.include_router(paymentTypes.router)
app.include_router(slots.router)


@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в API для школы танцев!",
        "docs": "/docs",
        "endpoints": [
            "/auth",
            "/users"
            "/events"
            "/eventTypes"
        ]
    }
