# Dance Studio API

RESTful API на базе FastAPI для школы танцев.

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/dance-fast-api.git
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
   uvicorn app.main:app --reload --port 8000
   ```

5. Откройте браузер и перейдите на http://localhost:8000/docs для доступа к документации Swagger.
