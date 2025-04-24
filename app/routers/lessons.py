import uuid
from datetime import timezone, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, Query
from typing import List

from app.auth.jwt import get_current_admin, get_current_teacher, get_current_student, get_current_user
from app.database import get_db
from app import models, schemas
from app.routers.classrooms import search_available_classrooms

router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
    responses={404: {"description": "Занятие не найдено"}}
)


async def check_classroom(classroom_id, start_time, finish_time, are_neighbours_allowed, db: Session):
    classroom = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зал не найден"
        )

    available_classrooms = await search_available_classrooms(schemas.ClassroomSearch(
        date_from=start_time,
        date_to=finish_time,
        are_neighbours_allowed=are_neighbours_allowed
    ), db=db)

    if classroom not in available_classrooms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Зал занят"
        )


async def check_lesson_data(
        lesson_data,
        is_group,
        db: Session,
        existing_lesson = None
):
    start_time = lesson_data.start_time if lesson_data.start_time else existing_lesson.start_time
    finish_time = lesson_data.finish_time if lesson_data.finish_time else existing_lesson.finish_time
    if start_time >= finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начало занятия должно быть раньше его конца"
        )
    if start_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Запрещено создавать занятия в прошлом"
        )

    if lesson_data.lesson_type_id:
        lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_data.lesson_type_id).first()
        if not lesson_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тип занятия не найден"
            )
        if lesson_type.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип занятия не активен"
            )
        if is_group and not lesson_type.is_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Выбранный тип занятия является индивидуальным"
            )
        if not is_group and lesson_type.is_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Выбранный тип занятия является групповым"
            )

    are_neighbours_allowed = lesson_data.are_neighbours_allowed if type(lesson_data.are_neighbours_allowed) is bool \
        else existing_lesson.are_neighbours_allowed
    if 'classroom_id' in lesson_data.model_dump(exclude_none=True):
        await check_classroom(
            lesson_data.classroom_id, start_time, finish_time, are_neighbours_allowed, db
        )


def get_and_check_group(group_id, db: Session):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    if group.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Группа не активна"
        )
    return group


def create_subscription(student_id, lesson_type_id, db: Session):
    subscription_template = db.query(models.SubscriptionTemplate).join(
        models.SubscriptionLessonType
    ).filter(
        or_(
            models.SubscriptionTemplate.expiration_date == None,
            models.SubscriptionTemplate.expiration_date > datetime.now(timezone.utc)
        ),
        models.SubscriptionLessonType.lesson_type_id == lesson_type_id
    ).order_by(
        models.SubscriptionTemplate.price
    ).first()

    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подходящий абонемент не найден. Обратитесь в службу поддержки"
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
        lessons = lessons.join(models.Group).filter(models.Group.level_id.in_(filters.level_ids))

    if filters.dance_style_ids:
        lessons = lessons.join(models.LessonType).filter(
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
            models.LessonSubscription
        ).join(
            models.Subscription
        ).filter(
            models.Subscription.student_id.in_(filters.student_ids)
        )

    if filters.teacher_ids:
        lessons = lessons.join(
            models.TeacherLesson
        ).filter(
            models.TeacherLesson.teacher_id.in_(filters.teacher_ids)
        )

    return lessons


def get_teacher_parallel_lesson(teacher_id, start_time, finish_time, db: Session):
    teacher_parallel_lesson = db.query(models.Lesson).join(
        models.TeacherLesson, and_(
            models.TeacherLesson.teacher_id == teacher_id,
            models.TeacherLesson.lesson_id == models.Lesson.id
        )
    ).filter(
        models.Lesson.terminated == False,
        or_(
            and_(start_time >= models.Lesson.start_time,
                 start_time < models.Lesson.finish_time),
            and_(finish_time > models.Lesson.start_time,
                 finish_time <= models.Lesson.finish_time),
            and_(start_time <= models.Lesson.start_time,
                 finish_time >= models.Lesson.finish_time)
        )
    ).first()
    return teacher_parallel_lesson


def get_student_parallel_lesson(student_id, start_time, finish_time, db: Session):
    student_parallel_lesson = db.query(models.Lesson).join(
        models.LessonSubscription, and_(
            models.LessonSubscription.lesson_id == models.Lesson.id,
            models.LessonSubscription.cancelled == False
        )
    ).join(models.Subscription).filter(
        models.Subscription.student_id == student_id,
        models.Lesson.terminated == False,
        or_(
            and_(start_time >= models.Lesson.start_time,
                 start_time < models.Lesson.finish_time),
            and_(finish_time > models.Lesson.start_time,
                 finish_time <= models.Lesson.finish_time),
            and_(start_time <= models.Lesson.start_time,
                 finish_time >= models.Lesson.finish_time)
        )
    ).first()
    return student_parallel_lesson


@router.post("/", response_model=schemas.LessonInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        lesson_data: schemas.LessonBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    await check_lesson_data(lesson_data, lesson_data.group_id, db)

    if lesson_data.group_id:
        get_and_check_group(lesson_data.group_id, db)

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


@router.post("/individual", response_model=schemas.LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_individual_lesson(
        lesson_data: schemas.LessonIndividual,
        current_teacher: models.Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    await check_lesson_data(lesson_data, False, db)

    student = db.query(models.Student).filter(models.Student.id == lesson_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )
    if student.user.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт ученика деактивирован"
        )

    subscription = create_subscription(student.id, lesson_data.lesson_type_id, db)

    parallel_teacher_lesson = get_teacher_parallel_lesson(
        current_teacher.id, lesson_data.start_time, lesson_data.finish_time, db
    )
    if parallel_teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель уже связан с пересекающимся по времени занятием"
        )

    parallel_student_lesson = get_student_parallel_lesson(
        student.id, lesson_data.start_time, lesson_data.finish_time, db
    )
    if parallel_student_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ученик уже записан на пересекающееся по времени занятие"
        )

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
    await check_lesson_data(lesson_data, True, db)

    group = get_and_check_group(lesson_data.group_id, db)
    if current_teacher not in group.teachers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель не связан с данной группой"
        )

    parallel_lesson = get_teacher_parallel_lesson(
        current_teacher.id,
        lesson_data.start_time,
        lesson_data.finish_time,
        db
    )
    if parallel_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель уже связан с пересекающимся по времени занятием"
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
    await check_lesson_data(lesson_data, False, db)

    teacher = db.query(models.Teacher).filter(models.Teacher.id == lesson_data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )
    if teacher.user.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт преподавателя деактивирован"
        )

    teacher_lesson_type = db.query(models.TeacherLessonType).filter(
        models.TeacherLessonType.teacher_id == teacher.id,
        models.TeacherLessonType.lesson_type_id == lesson_data.lesson_type_id
    ).first()
    if not teacher_lesson_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Учитель не преподаёт данный вид занятий"
        )

    subscription = create_subscription(current_student.id, lesson_data.lesson_type_id, db)

    parallel_lesson = get_teacher_parallel_lesson(
        teacher.id,
        lesson_data.start_time,
        lesson_data.finish_time,
        db
    )
    if parallel_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель уже связан с пересекающимся по времени занятием"
        )

    parallel_student_lesson = get_student_parallel_lesson(
        current_student.id, lesson_data.start_time, lesson_data.finish_time, db
    )
    if parallel_student_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ученик уже записан на пересекающееся по времени занятие"
        )

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
    request = db.query(models.Lesson).filter(
        models.Lesson.id == lesson_id,
        models.Lesson.is_confirmed == False,
        models.Lesson.terminated == False
    ).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    teacher_lesson = db.query(models.TeacherLesson).filter(
        models.TeacherLesson.lesson_id == lesson_id,
        models.TeacherLesson.teacher_id == current_teacher.id
    ).first()
    if not teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель не связан с данной заявкой"
        )

    if response.is_confirmed:
        if not response.classroom_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Зал не указан"
            )
        await check_classroom(
            response.classroom_id, request.start_time, request.finish_time, request.are_neighbours_allowed, db
        )
        request.classroom_id = response.classroom_id
        request.is_confirmed = True
    else:
        request.terminated = True

    db.commit()
    db.refresh(request)

    return request


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
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    filters.is_group = True
    filters.student_ids = []

    lessons = db.query(models.Lesson)
    lessons = apply_filters_to_lessons(lessons, filters)
    lessons = lessons.offset(skip).limit(limit).all()

    return lessons


@router.get("/{lesson_id}", response_model=schemas.LessonInfo)
async def get_lesson_by_id(
        lesson_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )
    return lesson


@router.get("/full-info/{lesson_id}", response_model=schemas.LessonFullInfo)
async def get_lesson_full_info_by_id(
        lesson_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )
    return lesson


@router.patch("/{lesson_id}", response_model=schemas.LessonFullInfo, status_code=status.HTTP_200_OK)
async def patch_lesson(
        lesson_id: uuid.UUID,
        lesson_data: schemas.LessonUpdate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    await check_lesson_data(lesson_data, lesson_data.group_id or lesson.group_id, db, existing_lesson=lesson)

    if lesson_data.group_id:
        get_and_check_group(lesson_data.group_id, db)
    elif 'group_id' in lesson_data:
        lesson.group_id = None

    if 'classroom_id' in lesson_data and lesson_data.classroom_id is None:
        lesson.classroom_id = None

    for field, value in lesson_data.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)

    return lesson
