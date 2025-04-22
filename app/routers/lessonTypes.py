from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, Query
from typing import List
from app import schemas, models
from app.database import get_db

import uuid


router = APIRouter(
    prefix="/lessonTypes",
    tags=["lesson types"],
    responses={404: {"description": "Тип занятия не найден"}}
)


@router.post("/", response_model=schemas.LessonTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson_type(
        lesson_type_data: schemas.LessonTypeBase,
        db: Session = Depends(get_db)
):
    lesson_type = models.LessonType(
        dance_style_id=lesson_type_data.dance_style_id,
        is_group=lesson_type_data.is_group
    )

    db.add(lesson_type)
    db.commit()
    db.refresh(lesson_type)

    return lesson_type


def apply_filters_to_lesson_types(lesson_types: Query, filters):
    if filters.dance_style_ids:
        lesson_types = lesson_types.filter(models.LessonType.dance_style_id.in_(filters.dance_style_ids))
    if type(filters.is_group) is bool:
        lesson_types = lesson_types.filter(models.LessonType.is_group == filters.is_group)
    if type(filters.terminated) is bool:
        lesson_types = lesson_types.filter(models.LessonType.terminated == filters.terminated)

    return lesson_types


@router.post("/search", response_model=List[schemas.LessonTypeInfo])
async def search_lesson_types(
        filters: schemas.LessonTypeSearch,
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    lesson_types = db.query(models.LessonType)
    lesson_types = apply_filters_to_lesson_types(lesson_types, filters)
    lesson_types = lesson_types.offset(skip).limit(limit).all()
    return lesson_types


@router.post("/search/full-info", response_model=List[schemas.LessonTypeFullInfo])
async def search_lesson_types_full_info(
        filters: schemas.LessonTypeSearch,
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    lesson_types = db.query(models.LessonType)
    lesson_types = apply_filters_to_lesson_types(lesson_types, filters)
    lesson_types = lesson_types.offset(skip).limit(limit).all()
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


@router.get("/full-info/{lesson_type_id}", response_model=schemas.LessonTypeFullInfo)
async def get_lesson_type_full_info_by_id(lesson_type_id: uuid.UUID, db: Session = Depends(get_db)):
    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )
    return lesson_type


@router.patch("/{lesson_type_id}", response_model=schemas.LessonTypeFullInfo, status_code=status.HTTP_200_OK)
async def patch_lesson_type(
        lesson_type_id: uuid.UUID,
        lesson_type_data: schemas.LessonTypeUpdate,
        db: Session = Depends(get_db)
):
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
