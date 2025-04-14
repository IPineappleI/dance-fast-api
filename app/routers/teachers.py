import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin

router = APIRouter(
    prefix="/teachers",
    tags=["teachers"],
    responses={404: {"description": "Преподаватель не найден"}}
)


@router.post("/", response_model=schemas.TeacherInfo, status_code=status.HTTP_201_CREATED)
async def create_teacher(
        teacher_data: schemas.TeacherBase,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == teacher_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователя с идентификатором {teacher_data.user_id} не существует",
        )

    teacher = models.Teacher(
        user_id=teacher_data.user_id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher


@router.get("/", response_model=List[schemas.TeacherInfo])
async def get_all_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/full-info", response_model=List[schemas.TeacherFullInfo])
async def get_all_teachers_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/{teacher_id}", response_model=schemas.TeacherInfo)
async def get_teacher_by_id(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )
    return teacher


@router.get("/full-info/{teacher_id}", response_model=schemas.TeacherFullInfo)
async def get_teacher_full_info_by_id(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    return teacher


@router.patch("/{teacher_id}", response_model=schemas.TeacherInfo, status_code=status.HTTP_200_OK)
async def patch_teacher(teacher_id: uuid.UUID, teacher_data: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    if teacher_data.user_id:
        user = db.query(models.User).filter(models.User.id == teacher_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден",
            )

    for field, value in teacher_data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)

    db.commit()
    db.refresh(teacher)

    return teacher
