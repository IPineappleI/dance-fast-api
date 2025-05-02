from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import or_, and_, text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_teacher, get_current_student, get_current_user
from app.database import get_db, TIMEZONE
from app.routers.classrooms import search_available_classrooms
from app.models import User, Admin, Teacher, Student, Group, Lesson, LessonType, Classroom
from app.models import Subscription, SubscriptionTemplate
from app.models.association import *
from app.schemas import SlotAvailableFilters
from app.schemas.lesson import *
from app.schemas.classroom import *

router = APIRouter(
    prefix='/lessons',
    tags=['lessons']
)


async def check_classroom(classroom_id, start_time, finish_time, are_neighbours_allowed, db: Session):
    start_time = start_time.astimezone(TIMEZONE)
    finish_time = finish_time.astimezone(TIMEZONE)

    classroom = db.query(Classroom).where(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Зал не найден'
        )
    if classroom.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Зал не активен'
        )

    available_classrooms = await search_available_classrooms(ClassroomAvailableFilters(
        date_from=start_time,
        date_to=finish_time,
        are_neighbours_allowed=are_neighbours_allowed
    ), db=db)
    available_classroom_ids = [available_classroom.id for available_classroom in available_classrooms.classrooms]
    if classroom.id not in available_classroom_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Зал занят'
        )


async def check_lesson_data(lesson_data, is_group, db: Session, existing_lesson=None):
    if lesson_data.start_time:
        lesson_data.start_time = lesson_data.start_time.astimezone(TIMEZONE)
    if lesson_data.finish_time:
        lesson_data.finish_time = lesson_data.finish_time.astimezone(TIMEZONE)

    start_time = lesson_data.start_time if lesson_data.start_time else existing_lesson.start_time
    finish_time = lesson_data.finish_time if lesson_data.finish_time else existing_lesson.finish_time
    if start_time >= finish_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Начало занятия должно быть раньше его конца'
        )
    if not existing_lesson and start_time < datetime.now(TIMEZONE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Запрещено создавать занятия в прошлом'
        )

    if lesson_data.lesson_type_id:
        lesson_type = db.query(LessonType).where(LessonType.id == lesson_data.lesson_type_id).first()
        if not lesson_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Тип занятия не найден'
            )
        if lesson_type.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Тип занятия не активен'
            )
        if is_group and not lesson_type.is_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Выбранный тип занятия является индивидуальным'
            )
        if not is_group and lesson_type.is_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Выбранный тип занятия является групповым'
            )
    elif existing_lesson and 'group_id' in lesson_data.model_dump(exclude_unset=True):
        if existing_lesson.lesson_type.is_group and not lesson_data.group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='У группового занятия обязательно должна быть группа'
            )
        if not existing_lesson.lesson_type.is_group and lesson_data.group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='У индивидуального занятия не может быть группы'
            )

    lesson_data_classroom_check = 'classroom_id' in lesson_data.model_dump(exclude_unset=True)

    classroom_id = lesson_data.classroom_id if lesson_data_classroom_check \
        else (existing_lesson.classroom_id if existing_lesson else None)

    if classroom_id and (lesson_data_classroom_check or lesson_data.start_time or lesson_data.finish_time):
        are_neighbours_allowed = lesson_data.are_neighbours_allowed if lesson_data.are_neighbours_allowed is not None \
            else existing_lesson.are_neighbours_allowed

        await check_classroom(classroom_id, start_time, finish_time, are_neighbours_allowed, db)


def get_and_check_group(group_id, db: Session):
    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )
    if group.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Группа не активна'
        )
    return group


def create_subscription(student_id, lesson_type_id, db: Session):
    subscription_template = db.query(SubscriptionTemplate).where(
        db.query(SubscriptionLessonType).where(
            SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id,
            SubscriptionLessonType.lesson_type_id == lesson_type_id,
            or_(
                SubscriptionTemplate.expiration_date == None,
                SubscriptionTemplate.expiration_date > datetime.now(TIMEZONE)
            )
        ).exists()
    ).order_by(
        SubscriptionTemplate.price
    ).first()

    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Подходящий абонемент не найден. Обратитесь в службу поддержки'
        )

    subscription = Subscription(
        student_id=student_id,
        subscription_template_id=subscription_template.id
    )
    if subscription_template.expiration_day_count:
        subscription.expiration_date = (
                datetime.now(TIMEZONE) + timedelta(days=subscription_template.expiration_day_count)
        )

    db.add(subscription)

    return subscription


def get_teacher_parallel_lesson(teacher_id, start_time, finish_time, db: Session):
    start_time = start_time.astimezone(TIMEZONE)
    finish_time = finish_time.astimezone(TIMEZONE)
    teacher_parallel_lesson = db.query(Lesson).where(
        db.query(TeacherLesson).where(
            TeacherLesson.lesson_id == Lesson.id,
            TeacherLesson.teacher_id == teacher_id,
            Lesson.terminated == False,
            or_(
                and_(start_time >= Lesson.start_time,
                     start_time < Lesson.finish_time),
                and_(finish_time > Lesson.start_time,
                     finish_time <= Lesson.finish_time),
                and_(start_time <= Lesson.start_time,
                     finish_time >= Lesson.finish_time)
            )
        ).exists()
    ).first()
    return teacher_parallel_lesson


def get_student_parallel_lesson(student_id, start_time, finish_time, db: Session):
    start_time = start_time.astimezone(TIMEZONE)
    finish_time = finish_time.astimezone(TIMEZONE)
    student_parallel_lesson = db.query(Lesson).where(
        Lesson.terminated == False,
        db.query(LessonSubscription).where(
            LessonSubscription.lesson_id == Lesson.id,
            LessonSubscription.cancelled == False
        ).join(Subscription).where(
            Subscription.student_id == student_id,
            or_(
                and_(start_time >= Lesson.start_time,
                     start_time < Lesson.finish_time),
                and_(finish_time > Lesson.start_time,
                     finish_time <= Lesson.finish_time),
                and_(start_time <= Lesson.start_time,
                     finish_time >= Lesson.finish_time)
            )
        ).exists()
    ).first()
    return student_parallel_lesson


@router.post('/', response_model=LessonInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        lesson_data: LessonCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if lesson_data.group_id:
        get_and_check_group(lesson_data.group_id, db)

    await check_lesson_data(lesson_data, lesson_data.group_id, db)

    lesson = Lesson(
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


@router.post('/individual', response_model=LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_individual_lesson(
        lesson_data: LessonCreateIndividual,
        current_teacher: Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == lesson_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ученик не найден'
        )
    if student.user.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Аккаунт ученика деактивирован'
        )

    await check_lesson_data(lesson_data, False, db)

    subscription = create_subscription(student.id, lesson_data.lesson_type_id, db)

    parallel_teacher_lesson = get_teacher_parallel_lesson(
        current_teacher.id, lesson_data.start_time, lesson_data.finish_time, db
    )
    if parallel_teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель уже связан с пересекающимся по времени занятием'
        )

    parallel_student_lesson = get_student_parallel_lesson(
        student.id, lesson_data.start_time, lesson_data.finish_time, db
    )
    if parallel_student_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ученик уже записан на пересекающееся по времени занятие'
        )

    lesson = Lesson(
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

    lesson_subscription = LessonSubscription(
        lesson_id=lesson.id,
        subscription_id=subscription.id
    )
    db.add(lesson_subscription)

    teacher_lesson = TeacherLesson(
        teacher_id=current_teacher.id,
        lesson_id=lesson.id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.post('/group', response_model=LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_group_lesson(
        lesson_data: LessonCreateGroup,
        current_teacher: Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    group = get_and_check_group(lesson_data.group_id, db)
    if current_teacher not in group.teachers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель не связан с данной группой'
        )

    await check_lesson_data(lesson_data, True, db)

    parallel_lesson = get_teacher_parallel_lesson(
        current_teacher.id,
        lesson_data.start_time,
        lesson_data.finish_time,
        db
    )
    if parallel_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель уже связан с пересекающимся по времени занятием'
        )

    lesson = Lesson(
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

    teacher_lesson = TeacherLesson(
        teacher_id=current_teacher.id,
        lesson_id=lesson.id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.post('/request', response_model=LessonFullInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson_request(
        lesson_data: LessonCreateRequest,
        current_student: Student = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == lesson_data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )
    if teacher.user.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Аккаунт преподавателя деактивирован'
        )

    await check_lesson_data(lesson_data, False, db)

    slots = await search_available_slots(SlotAvailableFilters(
        date_from=lesson_data.start_time,
        date_to=lesson_data.finish_time,
        teacher_ids=[teacher.id],
        lesson_type_ids=[lesson_data.lesson_type_id]
    ), current_student.user, db)
    if (len(slots) != 1 or
            lesson_data.start_time < slots[0].start_time or lesson_data.finish_time > slots[0].finish_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='У учителя нет подходящего слота, или учитель не преподаёт данный вид занятий'
        )

    subscription = create_subscription(current_student.id, lesson_data.lesson_type_id, db)

    parallel_student_lesson = get_student_parallel_lesson(
        current_student.id, lesson_data.start_time, lesson_data.finish_time, db
    )
    if parallel_student_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ученик уже записан на пересекающееся по времени занятие'
        )

    lesson = Lesson(
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

    lesson_subscription = LessonSubscription(
        lesson_id=lesson.id,
        subscription_id=subscription.id
    )
    db.add(lesson_subscription)

    teacher_lesson = TeacherLesson(
        teacher_id=lesson_data.teacher_id,
        lesson_id=lesson.id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.patch('/request/{lesson_id}', response_model=LessonFullInfo)
async def respond_to_lesson_request(
        lesson_id: uuid.UUID,
        response: LessonResponse,
        current_teacher: Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    request = db.query(Lesson).where(
        Lesson.id == lesson_id,
        Lesson.is_confirmed == False,
        Lesson.terminated == False
    ).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Заявка не найдена'
        )

    teacher_lesson = db.query(TeacherLesson).where(
        TeacherLesson.lesson_id == lesson_id,
        TeacherLesson.teacher_id == current_teacher.id
    ).first()
    if not teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель не связан с данной заявкой'
        )

    if response.is_confirmed:
        if not response.classroom_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Зал не указан'
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


def apply_filters_to_lessons(lessons, filters, db):
    if filters.date_from:
        filters.date_from = filters.date_from.astimezone(TIMEZONE)
        lessons = lessons.where(Lesson.start_time >= filters.date_from)
    if filters.date_to:
        filters.date_to = filters.date_to.astimezone(TIMEZONE)
        lessons = lessons.where(Lesson.finish_time <= filters.date_to)

    if filters.is_confirmed is not None:
        lessons = lessons.where(Lesson.is_confirmed == filters.is_confirmed)
    if filters.terminated is not None:
        lessons = lessons.where(Lesson.terminated == filters.terminated)
    if filters.are_neighbours_allowed is not None:
        lessons = lessons.where(Lesson.are_neighbours_allowed == filters.are_neighbours_allowed)
    if filters.is_group is not None:
        lessons = lessons.where((Lesson.group_id != None) == filters.is_group)

    if filters.lesson_type_ids:
        lessons = lessons.where(Lesson.lesson_type_id.in_(filters.lesson_type_ids))
    if filters.classroom_ids:
        lessons = lessons.where(Lesson.classroom_id.in_(filters.classroom_ids))
    if filters.group_ids:
        lessons = lessons.where(Lesson.group_id.in_(filters.group_ids))

    if filters.level_ids:
        lessons = lessons.join(Group).where(Group.level_id.in_(filters.level_ids))

    if filters.dance_style_ids:
        lessons = lessons.join(LessonType).where(
            LessonType.dance_style_id.in_(filters.dance_style_ids)
        )

    if filters.subscription_template_ids:
        lessons = lessons.where(
            db.query(SubscriptionLessonType).where(
                SubscriptionLessonType.lesson_type_id == Lesson.lesson_type_id,
                SubscriptionLessonType.subscription_template_id.in_(filters.subscription_template_ids)
            ).exists()
        )

    if filters.teacher_ids:
        lessons = lessons.where(
            db.query(TeacherLesson).where(
                TeacherLesson.lesson_id == Lesson.id,
                TeacherLesson.teacher_id.in_(filters.teacher_ids)
            ).exists()
        )

    if filters.student_ids:
        lessons = lessons.where(
            db.query(LessonSubscription).where(
                LessonSubscription.lesson_id == Lesson.id,
                LessonSubscription.cancelled == False
            ).join(Subscription).where(
                Subscription.student_id.in_(filters.student_ids)
            ).exists()
        )

    return lessons


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'start_time', 'finish_time', 'is_confirmed', 'are_neighbours_allowed',
                        'created_at', 'terminated'], 'Данная сортировка невозможна'
    return order_by


@router.post('/search/admin', response_model=LessonPage)
async def search_lessons_admin(
        filters: LessonFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lessons = db.query(Lesson)
    lessons = apply_filters_to_lessons(lessons, filters, db)
    return LessonPage(
        lessons=lessons.order_by(
            text('lessons.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lessons.count()
    )


@router.post('/search/admin/full-info', response_model=LessonFullInfoPage)
async def search_lessons_admin_full_info(
        filters: LessonFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lessons = db.query(Lesson)
    lessons = apply_filters_to_lessons(lessons, filters, db)
    return LessonFullInfoPage(
        lessons=lessons.order_by(
            text('lessons.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lessons.count()
    )


@router.post('/search/teacher', response_model=LessonFullInfoPage)
async def search_teacher_lessons(
        filters: LessonFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_teacher: Teacher = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    filters.teacher_ids = [current_teacher.id]

    lessons = db.query(Lesson)
    lessons = apply_filters_to_lessons(lessons, filters, db)
    return LessonFullInfoPage(
        lessons=lessons.order_by(
            text('lessons.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lessons.count()
    )


@router.post('/search/student', response_model=LessonFullInfoPage)
async def search_student_lessons(
        filters: LessonFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_student: Student = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    filters.student_ids = [current_student.id]

    lessons = db.query(Lesson)
    lessons = apply_filters_to_lessons(lessons, filters, db)
    return LessonFullInfoPage(
        lessons=lessons.order_by(
            text('lessons.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lessons.count()
    )


@router.post('/search/group', response_model=LessonFullInfoPage)
async def search_group_lessons(
        filters: LessonFiltersGroup,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    filters.is_group = True
    filters.student_ids = []

    lessons = db.query(Lesson)
    lessons = apply_filters_to_lessons(lessons, filters, db)

    if filters.is_participant is not None:
        if current_user.teacher:
            lessons = lessons.where(
                db.query(TeacherLesson).where(
                    TeacherLesson.lesson_id == Lesson.id,
                    TeacherLesson.teacher_id == current_user.teacher.id
                ).exists() == filters.is_participant
            )
        elif current_user.student:
            lessons = lessons.where(
                db.query(LessonSubscription).where(
                    LessonSubscription.lesson_id == Lesson.id,
                    LessonSubscription.cancelled == False
                ).join(Subscription).where(
                    Subscription.student_id == current_user.student.id
                ).exists() == filters.is_participant
            )

    return LessonFullInfoPage(
        lessons=lessons.order_by(
            text('lessons.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lessons.count()
    )


@router.get('/{lesson_id}', response_model=LessonInfo)
async def get_lesson_by_id(
        lesson_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )
    return lesson


@router.get('/full-info/{lesson_id}', response_model=LessonWithSubscriptions)
async def get_lesson_full_info_by_id(
        lesson_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )

    if current_user.student:
        if current_user.student not in lesson.actual_students:
            lesson.fitting_subscriptions = [subscription for subscription in current_user.student.subscriptions
                                            if lesson.lesson_type in subscription.subscription_template.lesson_types
                                            and subscription.lessons_left > 0 and
                                            (not subscription.expiration_date
                                             or subscription.expiration_date > datetime.now(TIMEZONE))]
        else:
            lesson.used_subscription = [subscription for subscription in current_user.student.subscriptions
                                        if lesson in subscription.lessons][0]

    return lesson


@router.patch('/{lesson_id}', response_model=LessonFullInfo)
async def patch_lesson(
        lesson_id: uuid.UUID,
        lesson_data: LessonUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )

    if lesson_data.group_id:
        get_and_check_group(lesson_data.group_id, db)

    group_id = lesson_data.group_id if 'group_id' in lesson_data.model_dump(exclude_unset=True) \
        else lesson.group_id

    await check_lesson_data(lesson_data, group_id, db, existing_lesson=lesson)

    for field, value in lesson_data.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)

    return lesson


from app.routers.slots import search_available_slots
