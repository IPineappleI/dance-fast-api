import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin
from app.auth.password import get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Пользователь не найден"}}
)


@router.post("/", response_model=schemas.UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь с таким email
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже используется",
        )
    # Проверяем, существует ли пользователь с таким phone_number
    db_user = db.query(models.User).filter(models.User.phone_number == user_data.phone_number).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Номер телефона уже используется",
        )

    # Создаем пользователя
    hashed_password = get_password_hash(user_data.password)

    user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        middle_name=user_data.middle_name,
        last_name=user_data.last_name,
        description=user_data.description,
        phone_number=user_data.phone_number,
        created_at=datetime.now(timezone.utc)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/", response_model=List[schemas.UserBase])
async def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=schemas.UserBase)
async def get_user_by_id(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return db_user


@router.patch("/{user_id}", response_model=schemas.UserBase, status_code=status.HTTP_200_OK)
async def patch_user(user_id: uuid.UUID, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    if user_data.email:
        email = db.query(models.User).filter(models.User.email == user_data.email).first()
        if email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже используется",
            )

    if user_data.phone_number:
        phone = db.query(models.User).filter(models.User.phone_number == user_data.phone_number).first()
        if phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Номер телефона уже используется",
            )

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user
