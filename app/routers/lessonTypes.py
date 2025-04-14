from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db

import uuid

router = APIRouter(
    prefix="/lessonTypes",
    tags=["lesson types"],
    responses={404: {"description": "Тип занятия не найден"}}
    # dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=schemas.LessonTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson_type(
        lesson_type_data: schemas.LessonTypeBase,
        db: Session = Depends(get_db)
):
    lesson_type = models.LessonType(
        name=lesson_type_data.name,
        description=lesson_type_data.description,
        created_at=datetime.now(timezone.utc)
    )

    db.add(lesson_type)
    db.commit()
    db.refresh(lesson_type)

    return lesson_type


@router.get("/", response_model=List[schemas.LessonTypeInfo])
async def get_all_lesson_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lesson_types = db.query(models.LessonType).offset(skip).limit(limit).all()
    return lesson_types


@router.get("/{lesson_type_id}", response_model=schemas.LessonTypeInfo)
async def get_lesson_type_by_id(lesson_type_id: uuid.UUID, db: Session = Depends(get_db)):
    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )
    return lesson_type


@router.patch("/{lesson_type_id}", response_model=schemas.LessonTypeInfo, status_code=status.HTTP_200_OK)
async def patch_lesson_type(lesson_type_id: uuid.UUID, lesson_type_data: schemas.LessonTypeUpdate, db: Session = Depends(get_db)):
    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )

    for field, value in lesson_type_data.model_dump(exclude_unset=True).items():
        setattr(lesson_type, field, value)

    db.commit()
    db.refresh(lesson_type)

    return lesson_type
