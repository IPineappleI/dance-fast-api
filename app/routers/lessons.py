import uuid
from datetime import timezone, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, Query
from typing import List

from app.auth.jwt import get_current_admin, get_current_teacher, get_current_student
from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
    responses={404: {"description": "Занятие не найдено"}}
)


@router.post("/", response_model=schemas.LessonInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        lesson_data: schemas.LessonBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if lesson_data.start_time >= lesson_data.finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )

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
                detail="Группа не найдена"
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
        is_confirmed=lesson_data.is_confirmed
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return lesson


def create_subscription(student_id, lesson_type_id, db: Session):
    subscription_template = db.query(models.SubscriptionTemplate).join(
        models.SubscriptionLessonType,
        models.SubscriptionLessonType.subscription_template_id == models.SubscriptionTemplate.id
    ).filter(
        models.SubscriptionLessonType.lesson_type_id == lesson_type_id
    ).order_by(models.SubscriptionTemplate.price).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подходящий абонемент не найден"
        )

    subscription = models.Subscription(
        student_id=student_id,
        subscription_template_id=subscription_template.id
    )
    if subscription_template.expiration_day_count:
        subscription.expiration_date = (
                datetime.now(timezone.utc) + timedelta(days=subscription_template.expiration_day_count)
        )

    db.add(subscription)

    return subscription


@router.post("/individual", response_model=schemas.LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_individual_lesson(
        lesson_data: schemas.LessonIndividual,
        current_teacher: models.Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    if lesson_data.start_time >= lesson_data.finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )

    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_data.lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )
    if lesson_type.is_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранный тип занятия является групповым"
        )

    classroom = db.query(models.Classroom).filter(models.Classroom.id == lesson_data.classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зал не найден"
        )

    student = db.query(models.Student).filter(models.Student.id == lesson_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )

    subscription = create_subscription(student.id, lesson_type.id, db)

    lesson = models.Lesson(
        name=lesson_data.name,
        description=lesson_data.description,
        lesson_type_id=lesson_data.lesson_type_id,
        start_time=lesson_data.start_time,
        finish_time=lesson_data.finish_time,
        classroom_id=lesson_data.classroom_id,
        are_neighbours_allowed=lesson_data.are_neighbours_allowed,
        is_confirmed=True
    )
    db.add(lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        lesson_id=lesson.id,
        subscription_id=subscription.id
    )
    db.add(lesson_subscription)

    teacher_lesson = models.TeacherLesson(
        teacher_id=current_teacher.id,
        lesson_id=lesson.id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.post("/group", response_model=schemas.LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_group_lesson(
        lesson_data: schemas.LessonGroup,
        current_teacher: models.Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    if lesson_data.start_time >= lesson_data.finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )

    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_data.lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )
    if not lesson_type.is_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранный тип занятия является индивидуальным"
        )

    classroom = db.query(models.Classroom).filter(models.Classroom.id == lesson_data.classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зал не найден"
        )

    group = db.query(models.Group).join(
        models.TeacherGroup,
        models.TeacherGroup.teacher_id == current_teacher.id
    ).filter(and_(
        models.Group.id == lesson_data.group_id,
        models.TeacherGroup.teacher_id == current_teacher.id
    )).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    teacher_group = db.query(models.TeacherGroup).filter(and_(
        models.TeacherGroup.group_id == group.id,
        models.TeacherGroup.teacher_id == current_teacher.id
    )).first()
    if not teacher_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не связан с указанной группой"
        )

    lesson = models.Lesson(
        name=lesson_data.name,
        description=lesson_data.description,
        lesson_type_id=lesson_data.lesson_type_id,
        start_time=lesson_data.start_time,
        finish_time=lesson_data.finish_time,
        classroom_id=lesson_data.classroom_id,
        group_id=group.id,
        are_neighbours_allowed=lesson_data.are_neighbours_allowed,
        is_confirmed=True
    )
    db.add(lesson)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=current_teacher.id,
        lesson_id=lesson.id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.post("/request", response_model=schemas.LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson_request(
        lesson_data: schemas.LessonRequest,
        current_student: models.Student = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    if lesson_data.start_time >= lesson_data.finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )

    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_data.lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )
    if lesson_type.is_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранный тип занятия является групповым"
        )

    subscription = create_subscription(current_student.id, lesson_type.id, db)

    lesson = models.Lesson(
        name=lesson_data.name,
        description=lesson_data.description,
        lesson_type_id=lesson_data.lesson_type_id,
        start_time=lesson_data.start_time,
        finish_time=lesson_data.finish_time,
        are_neighbours_allowed=lesson_data.are_neighbours_allowed,
        is_confirmed=False
    )
    db.add(lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        lesson_id=lesson.id,
        subscription_id=subscription.id
    )
    db.add(lesson_subscription)

    teacher_lesson = models.TeacherLesson(
        teacher_id=lesson_data.teacher_id,
        lesson_id=lesson.id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.patch("/request/{lesson_id}", response_model=schemas.LessonFullInfo, status_code=status.HTTP_200_OK)
async def respond_to_lesson_request(
        lesson_id: uuid.UUID,
        response: schemas.LessonResponse,
        current_teacher: models.Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    request = db.query(models.Lesson).filter(and_(
        models.Lesson.id == lesson_id,
        ~models.Lesson.is_confirmed,
        ~models.Lesson.terminated
    )).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    teacher_lesson = db.query(models.TeacherLesson).filter(and_(
        models.TeacherLesson.lesson_id == lesson_id,
        models.TeacherLesson.teacher_id == current_teacher.id
    )).first()
    if not teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учитель не связан с данной заявкой"
        )

    if response.is_confirmed:
        if not response.classroom_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не указан"
            )
        classroom = db.query(models.Classroom).filter(models.Classroom.id == response.classroom_id).first()
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )
        request.classroom_id = classroom.id
        request.is_confirmed = response.is_confirmed
    else:
        request.terminated = True

    db.commit()
    db.refresh(request)

    return request


def apply_filters_to_lessons(lessons: Query, filters):
    if filters.date_from:
        lessons = lessons.filter(models.Lesson.start_time >= filters.date_from)
    if filters.date_to:
        lessons = lessons.filter(models.Lesson.finish_time <= filters.date_to)

    if type(filters.is_confirmed) is bool:
        lessons = lessons.filter(models.Lesson.is_confirmed == filters.is_confirmed)
    if type(filters.terminated) is bool:
        lessons = lessons.filter(models.Lesson.terminated == filters.terminated)
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

    if filters.level_ids:
        lessons = lessons.join(
            models.Group, models.Group.id == models.Lesson.group_id
        ).filter(models.Group.level_id.in_(filters.level_ids))

    if filters.dance_style_ids:
        lessons = lessons.join(models.LessonType, models.LessonType.id == models.Lesson.lesson_type_id).filter(
            models.LessonType.dance_style_id.in_(filters.dance_style_ids)
        )

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


@router.post("/search/admin", response_model=List[schemas.LessonInfo])
async def search_lessons_admin(
        filters: schemas.LessonSearch,
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()
    return lessons


@router.post("/search/admin/full-info", response_model=List[schemas.LessonFullInfo])
async def search_lessons_admin_full_info(
        filters: schemas.LessonSearch,
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()
    return lessons


@router.post("/search/teacher/full-info", response_model=List[schemas.LessonFullInfo])
async def search_lessons_teacher_full_info(
        filters: schemas.LessonSearch,
        skip: int = 0, limit: int = 100,
        current_teacher: models.Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    filters.teacher_ids = [current_teacher.id]

    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()

    return lessons


@router.post("/search/student/full-info", response_model=List[schemas.LessonWithSubscription])
async def search_lessons_student_full_info(
        filters: schemas.LessonSearch,
        skip: int = 0, limit: int = 100,
        current_student: models.Student = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    filters.student_ids = [current_student.id]

    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()

    return lessons


@router.post("/search/group/full-info", response_model=List[schemas.LessonFullInfo])
async def search_group_lessons_full_info(
        filters: schemas.LessonSearch,
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    filters.is_group = True
    filters.student_ids = []

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


@router.patch("/{lesson_id}", response_model=schemas.LessonFullInfo, status_code=status.HTTP_200_OK)
async def patch_lesson(
        lesson_id: uuid.UUID,
        lesson_data: schemas.LessonUpdate,
        db: Session = Depends(get_db)
):
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
