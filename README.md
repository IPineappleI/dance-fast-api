# Dance Studio API

RESTful API на базе FastAPI для школы танцев.

## Функциональность

- Управление пользователями
- Управление инструкторами (в разработке)
- Управление классами танцев (в разработке)
- Управление расписанием (в разработке)
- Бронирование занятий (в разработке)

## Требования

- Python 3.8+
- PostgreSQL 12+
- Зависимости из requirements.txt

## Настройка PostgreSQL

1. Установите PostgreSQL для вашей операционной системы:
   - Mac: `brew install postgresql` или [PostgreSQL.app](https://postgresapp.com/)
   - Windows: [Загрузите установщик](https://www.postgresql.org/download/windows/)
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. Создайте базу данных:
   ```sql
   CREATE DATABASE dance_api;
   ```

3. Создайте пользователя (или используйте существующего):
   ```sql
   CREATE USER dance_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE dance_api TO dance_user;
   ```

4. Обновите файл `.env` с вашими настройками базы данных:
   ```
   DATABASE_URL=postgresql://dance_user:your_password@localhost:5432/dance_api
   ```

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/dance-studio-api.git
   cd dance-studio-api
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

5. Откройте браузер и перейдите на http://localhost:8001/docs для доступа к Swagger UI документации.

## API Endpoints

- `GET /` - Главная страница API
- `GET /users` - Получить всех пользователей
- `GET /users/{id}` - Получить пользователя по ID
- `POST /users` - Создать нового пользователя 