from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config import settings
from app.database import get_db
from app.auth.password import verify_password, get_password_hash
from app.auth.jwt import create_token, get_current_user, verify_token
from app.email import send_email_confirmation_token
from app.models import User, Admin, Teacher, Student, Level
from app.schemas.token import *
from app.schemas.admin import *
from app.schemas.teacher import *
from app.schemas.student import *

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES = settings.EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix='/auth',
    tags=['authentication']
)


async def create_user(user_data, db: Session):
    email_user = db.query(User).where(User.email == user_data.email).first()
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email уже используется'
        )

    phone_user = db.query(User).where(User.phone_number == user_data.phone_number).first()
    if phone_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Номер телефона уже используется'
        )

    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        receive_email=user_data.receive_email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        description=user_data.description,
        phone_number=user_data.phone_number
    )
    db.add(user)

    db.commit()

    try:
        await send_email_confirmation_token(user.id, user.email, user.first_name)
    except Exception as e:
        db.query(User).where(User.id == user.id).delete()
        db.commit()
        raise e

    return user


async def patch_user(user_id, user_data: UserUpdate, db: Session):
    user = db.query(User).where(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )

    if user_data.old_password and user_data.new_password:
        if user_data.old_password == user_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Новый пароль должен отличаться от старого'
            )
        if not verify_password(user_data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Неверный пароль'
            )
        user.hashed_password = get_password_hash(user_data.new_password)

    if user_data.phone_number:
        phone_user = db.query(User).where(User.phone_number == user_data.phone_number).first()
        if phone_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Номер телефона уже используется'
            )

    if user_data.email:
        email_user = db.query(User).where(User.email == user_data.email).first()
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email уже используется'
            )
        await send_email_confirmation_token(user.id, user_data.email)
        user.email_confirmed = False

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()


@router.post('/register', response_model=StudentFullInfo, status_code=status.HTTP_201_CREATED)
async def register_student(
        student_data: StudentCreate,
        db: Session = Depends(get_db)
):
    level = db.query(Level).where(Level.id == student_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Уровень подготовки не найден'
        )
    if level.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Уровень подготовки не активен'
        )

    user = await create_user(student_data, db)

    student = Student(
        user_id=user.id,
        level_id=student_data.level_id,
        created_at=user.created_at
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


@router.get('/confirm-email/{confirmation_token}')
async def confirm_email(
        confirmation_token: str,
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Невалидный токен подтверждения адреса электронной почты',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token_data = verify_token(confirmation_token, credentials_exception)

    user = db.query(User).where(User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    if user.terminated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Ваш аккаунт был деактивирован'
        )

    user.email_confirmed = True
    db.commit()

    return 'Адрес электронной почты подтверждён успешно'


@router.post('/token', response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).where(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный email или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
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

    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_token(
        data={'user_id': str(user.id)},
        expires_delta=expires_delta
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=Union[StudentFullInfoWithRole, TeacherFullInfoWithRole, AdminFullInfoWithRole])
async def get_current_user_full_info(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.user_id == current_user.id).first()
    if student:
        student.role = 'student'
        return student

    teacher = db.query(Teacher).where(Teacher.user_id == current_user.id).first()
    if teacher:
        teacher.role = 'teacher'
        return teacher

    admin = db.query(Admin).where(Admin.user_id == current_user.id).first()
    if admin:
        admin.role = 'admin'
        return admin

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='У пользователя нет роли. Обратитесь в службу поддержки'
    )
