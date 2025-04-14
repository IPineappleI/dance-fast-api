import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Студент не найден"}}
)


@router.post("/", response_model=schemas.StudentInfo, status_code=status.HTTP_201_CREATED)
async def create_student(
        student_data: schemas.StudentBase,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == student_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователя с идентификатором {student_data.user_id} не существует",
        )

    level = db.query(models.Level).filter(models.Level.id == student_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Уровня подготовки с идентификатором {student_data.level_id} не существует",
        )

    student = models.Student(
        user_id=student_data.user_id,
        level_id=student_data.level_id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


@router.get("/", response_model=List[schemas.StudentInfo])
async def get_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/full-info", response_model=List[schemas.StudentFullInfo])
async def get_all_students_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=schemas.StudentInfo)
async def get_student_by_id(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден"
        )
    return student


@router.get("/full-info/{student_id}", response_model=schemas.StudentFullInfo)
async def get_student_full_info_by_id(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден"
        )

    return student


@router.patch("/{student_id}", response_model=schemas.StudentInfo, status_code=status.HTTP_200_OK)
async def patch_student(student_id: uuid.UUID, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден"
        )

    if student_data.user_id:
        user = db.query(models.User).filter(models.User.id == student_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден",
            )

    if student_data.level_id:
        level = db.query(models.Level).filter(models.Level.id == student_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Уровень не найден",
            )

    for field, value in student_data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student
