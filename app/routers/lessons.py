import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
    responses={404: {"description": "Занятие не найдено"}}
)


@router.post("/", response_model=schemas.LessonInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson(lesson_data: schemas.LessonBase, db: Session = Depends(get_db)):
    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_data.lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )

    classroom = db.query(models.Classroom).filter(models.Classroom.id == lesson_data.classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зал не найден"
        )

    group = db.query(models.Group).filter(models.Group.id == lesson_data.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    if lesson_data.start_time >= lesson_data.finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )

    lesson = models.Lesson(
        name=lesson_data.name,
        description=lesson_data.description,
        lesson_type_id=lesson_data.lesson_type_id,
        start_time=lesson_data.start_time,
        finish_time=lesson_data.finish_time,
        classroom_id=lesson_data.classroom_id,
        group_id=lesson_data.group_id,
        are_neighbours_allowed=lesson_data.are_neighbours_allowed,
        is_confirmed=True
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return lesson


@router.get("/", response_model=List[schemas.LessonInfo])
async def get_all_lessons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).offset(skip).limit(limit).all()
    return lessons


@router.get("/full-info", response_model=List[schemas.LessonFullInfo])
async def get_all_lessons_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).offset(skip).limit(limit).all()
    return lessons


@router.get("/{lesson_id}", response_model=schemas.LessonInfo)
async def get_lesson_by_id(lesson_id: uuid.UUID, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lessons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )
    return lessons


@router.get("/full-info/{lesson_id}", response_model=schemas.LessonFullInfo)
async def get_lesson_full_info_by_id(lesson_id: uuid.UUID, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lessons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )
    return lessons


@router.patch("/{lesson_id}", response_model=schemas.LessonInfo, status_code=status.HTTP_200_OK)
async def patch_lesson(
        lesson_id: uuid.UUID, lesson_data: schemas.LessonUpdate,
        db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    if lesson_data.lesson_type_id:
        lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_data.lesson_type_id).first()
        if not lesson_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тип занятия не найден"
            )

    if lesson_data.classroom_id:
        classroom = db.query(models.Classroom).filter(models.Classroom.id == lesson_data.classroom_id).first()
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )

    if lesson_data.group_id:
        group = db.query(models.Group).filter(models.Group.id == lesson_data.group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа не найдена",
            )

    for field, value in lesson_data.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)

    if lesson.start_time >= lesson.finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )

    db.commit()
    db.refresh(lesson)

    return lesson
