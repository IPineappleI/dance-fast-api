from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import timedelta

from app.database import get_db
from app.models import StudentGroup, Group, Subscription, SubscriptionTemplate, Payment, TeacherGroup, TeacherLessonType
from app.schemas.token import Token
from app.schemas.student import StudentInfo, StudentCreate
from app.models.user import User
from app.models.student import Student
from app.models.level import Level
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.auth.password import verify_password, get_password_hash
from app.auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post("/register", response_model=StudentInfo, status_code=status.HTTP_201_CREATED)
async def register(user_data: StudentCreate, db: Session = Depends(get_db)):
    """Регистрация нового студента."""
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        description=user_data.description,
        phone_number=user_data.phone_number,
        is_active=True
    )
    new_user.role = "student"
    new_user.level_name = db.query(Level).filter(Level.id == user_data.level_id).first().name

    # Сохраняем пользователя в базе данных
    db.add(new_user)
    db.commit()

    # Создаем запись в таблице student
    student = Student(
        user_id=new_user.id,
        level_id=user_data.level_id,
        created_at=new_user.created_at
    )

    db.add(student)
    db.commit()
    db.refresh(new_user)
    db.refresh(student)

    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Получение токена доступа."""
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == form_data.username).first()

    # Проверяем учетные данные пользователя
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Данный аккаунт был деактивирован",
        )

    # Создаем данные для токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Получение данных текущего пользователя."""
    student = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.level),
        joinedload(Student.groups).joinedload(StudentGroup.group).joinedload(Group.level),
        joinedload(Student.subscriptions).joinedload(Subscription.subscription_template)
        .joinedload(SubscriptionTemplate.lesson_types),
        joinedload(Student.subscriptions).joinedload(Subscription.payment).joinedload(Payment.payment_type)
    ).filter(Student.user_id == current_user.id).first()
    if student:
        student.role = "student"
        return student

    teacher = db.query(Teacher).options(
        joinedload(Teacher.user),
        joinedload(Teacher.groups).joinedload(TeacherGroup.group).joinedload(Group.level),
        joinedload(Teacher.lesson_types).joinedload(TeacherLessonType.lesson_type)
    ).filter(Teacher.user_id == current_user.id).first()
    if teacher:
        teacher.role = "teacher"
        return teacher

    admin = db.query(Admin).options(joinedload(Admin.user)).filter(Admin.user_id == current_user.id).first()
    if admin:
        admin.role = "admin"
        return admin

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Пользователь не найден"
    )
