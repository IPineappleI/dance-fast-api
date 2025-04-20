import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, Query
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


def apply_filters_to_lessons(lessons: Query, filters):
    if filters.date_from:
        lessons = lessons.filter(models.Lesson.start_time >= filters.date_from)
    if filters.date_to:
        lessons = lessons.filter(models.Lesson.finish_time <= filters.date_to)

    if type(filters.is_confirmed) is bool:
        lessons = lessons.filter(models.Lesson.is_confirmed == filters.is_confirmed)
    if type(filters.are_neighbours_allowed) is bool:
        lessons = lessons.filter(models.Lesson.are_neighbours_allowed == filters.are_neighbours_allowed)
    if type(filters.is_group) is bool:
        lessons = lessons.filter((models.Lesson.group_id != None) == filters.is_group)

    if filters.lesson_type_ids:
        lessons = lessons.filter(models.Lesson.lesson_type_id.in_(filters.lesson_type_ids))
    if filters.classroom_ids:
        lessons = lessons.filter(models.Lesson.classroom_id.in_(filters.classroom_ids))
    if filters.group_ids:
        lessons = lessons.filter(models.Lesson.group_id.in_(filters.group_ids))

    if filters.subscription_template_ids:
        lessons = lessons.join(
            models.SubscriptionLessonType,
            models.Lesson.lesson_type_id == models.SubscriptionLessonType.lesson_type_id
        ).filter(
            models.SubscriptionLessonType.subscription_template_id.in_(filters.subscription_template_ids)
        )

    if filters.student_ids:
        lessons = lessons.join(
            models.LessonSubscription,
            models.Lesson.id == models.LessonSubscription.lesson_id
        ).join(
            models.Subscription,
            models.LessonSubscription.subscription_id == models.Subscription.id
        ).filter(
            models.Subscription.student_id.in_(filters.student_ids)
        )

    if filters.teacher_ids:
        lessons = lessons.join(
            models.TeacherLesson,
            models.Lesson.id == models.TeacherLesson.lesson_id
        ).filter(
            models.TeacherLesson.teacher_id.in_(filters.teacher_ids)
        )

    return lessons


@router.post("/search", response_model=List[schemas.LessonInfo])
async def search_lessons(filters: schemas.LessonSearch,
                         skip: int = 0, limit: int = 100,
                         db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()

    return lessons


@router.post("/search/full-info", response_model=List[schemas.LessonFullInfo])
async def search_lessons_full_info(filters: schemas.LessonSearch,
                                   skip: int = 0, limit: int = 100,
                                   db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()

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
        lesson_id: uuid.UUID,
        lesson_data: schemas.LessonUpdate,
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
