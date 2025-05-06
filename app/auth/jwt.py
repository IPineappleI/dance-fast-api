from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, TIMEZONE
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.user import User
from app.models.admin import Admin
from app.schemas.token import TokenData

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()

    expiration_date = datetime.now(TIMEZONE) + expires_delta

    to_encode.update({'exp': expiration_date})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get('user_id')
        if user_id is None:
            raise credentials_exception

        return TokenData(id=user_id)

    except JWTError:
        raise credentials_exception


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Невалидные учётные данные',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token_data = verify_token(token, credentials_exception)

    user = db.query(User).where(User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    if user.terminated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Ваш аккаунт был деактивирован'
        )
    if not user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Пожалуйста, подтвердите адрес электронной почты'
        )

    return user


async def get_current_admin(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    admin = db.query(Admin).where(Admin.user_id == current_user.id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав',
        )
    return admin


async def get_current_teacher(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.user_id == current_user.id).first()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав',
        )
    return teacher


async def get_current_student(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.user_id == current_user.id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав',
        )
    return student
