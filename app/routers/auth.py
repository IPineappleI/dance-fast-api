from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import Student, Teacher, User, Admin, Level
from app.routers.users import create_user
from app.schemas import StudentFullInfoWithRole, TeacherFullInfoWithRole, AdminFullInfoWithRole
from app.schemas.student import StudentFullInfo, StudentCreate
from app.schemas.token import Token
from app.auth.password import verify_password, get_password_hash
from app.auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post("/register", response_model=StudentFullInfo, status_code=status.HTTP_201_CREATED)
async def register_student(
        student_data: StudentCreate,
        db: Session = Depends(get_db)
):
    level = db.query(Level).filter(Level.id == student_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уровень подготовки не найден"
        )
    if level.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Уровень подготовки не активен"
        )

    user = create_user(student_data, db)

    student = Student(
        user_id=user.id,
        level_id=student_data.level_id,
        created_at=user.created_at
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if user.terminated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ваш аккаунт был деактивирован"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=Union[StudentFullInfoWithRole, TeacherFullInfoWithRole, AdminFullInfoWithRole])
async def get_current_user_full_info(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if student:
        student.role = "student"
        return student

    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if teacher:
        teacher.role = "teacher"
        return teacher

    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if admin:
        admin.role = "admin"
        return admin

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="У пользователя нет роли. Обратитесь в службу поддержки"
    )
