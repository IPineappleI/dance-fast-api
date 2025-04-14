from passlib.context import CryptContext

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Проверяет, соответствует ли обычный пароль хешированному паролю."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Хеширует пароль."""
    return pwd_context.hash(password) 