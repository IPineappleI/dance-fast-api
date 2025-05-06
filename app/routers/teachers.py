from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db, TIMEZONE
from app.email import send_new_teacher_email, send_teacher_terminated_email
from app.routers.lessons import get_teacher_parallel_lesson
from app.routers.auth import create_user, patch_user
from app.models import User, Admin, Teacher, Group, Lesson, LessonType
from app.models.association import *
from app.schemas.teacher import *
from app.schemas import LessonFullInfo

router = APIRouter(
    prefix='/teachers',
    tags=['teachers']
)


def check_teacher(teacher, current_user):
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )
    if not current_user.admin and current_user.id != teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )


@router.post('/', response_model=TeacherInfo, status_code=status.HTTP_201_CREATED)
async def create_teacher(
        teacher_data: TeacherCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    user = await create_user(teacher_data, db)

    teacher = Teacher(
        user_id=user.id
    )

    db.add(teacher)
    db.commit()

    await send_new_teacher_email(teacher, db)

    db.refresh(teacher)

    return teacher


def apply_filters_to_teachers(teachers, filters, db):
    if filters.group_ids:
        teachers = teachers.where(
            db.query(TeacherGroup).where(
                TeacherGroup.teacher_id == Teacher.id,
                TeacherGroup.group_id.in_(filters.group_ids)
            ).exists()
        )

    if filters.lesson_type_ids:
        teachers = teachers.where(
            db.query(TeacherLessonType).where(
                TeacherLessonType.teacher_id == Teacher.id,
                TeacherLessonType.lesson_type_id.in_(filters.lesson_type_ids)
            ).exists()
        )

    if filters.terminated is not None:
        teachers = teachers.join(User).where(User.terminated == filters.terminated)

    return teachers


def check_order_by(order_by: str) -> str:
    assert order_by in ['created_at'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=TeacherPage)
async def search_teachers(
        filters: TeacherFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teachers = db.query(Teacher)
    teachers = apply_filters_to_teachers(teachers, filters, db)
    return TeacherPage(
        teachers=teachers.order_by(
            text('teachers.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=teachers.count()
    )


@router.post('/search/full-info', response_model=TeacherFullInfoPage)
async def search_teachers_full_info(
        filters: TeacherFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teachers = db.query(Teacher)
    teachers = apply_filters_to_teachers(teachers, filters, db)
    return TeacherFullInfoPage(
        teachers=teachers.order_by(
            text('teachers.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=teachers.count()
    )


@router.get('/{teacher_id}', response_model=TeacherInfo)
async def get_teacher_by_id(
        teacher_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )
    return teacher


@router.get('/full-info/{teacher_id}', response_model=TeacherFullInfo)
async def get_teacher_full_info_by_id(
        teacher_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )
    return teacher


@router.patch('/{teacher_id}', response_model=TeacherFullInfo)
async def patch_teacher(
        teacher_id: uuid.UUID,
        teacher_data: TeacherUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )
    if not current_user.admin and current_user.id != teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )

    if teacher_data.terminated:
        db.query(TeacherGroup).where(TeacherGroup.teacher_id == teacher_id).delete()

        db.query(TeacherLesson).where(
            TeacherLesson.teacher_id == teacher_id,
            db.query(Lesson).where(
                Lesson.id == TeacherLesson.lesson_id,
                Lesson.start_time >= datetime.now(TIMEZONE)
            ).exists()
        ).delete()

    old_terminated = teacher.user.terminated

    await patch_user(teacher.user_id, teacher_data, db)

    if teacher.user.terminated and not old_terminated:
        await send_teacher_terminated_email(teacher, db)
    elif not teacher.user.terminated and old_terminated:
        await send_new_teacher_email(teacher, db)

    db.refresh(teacher)

    return teacher


@router.post('/lesson-types/{teacher_id}/{lesson_type_id}', response_model=TeacherFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_teacher_lesson_type(
        teacher_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    check_teacher(teacher, current_user)

    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
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

    existing_lesson_type = db.query(TeacherLessonType).where(
        TeacherLessonType.teacher_id == teacher_id,
        TeacherLessonType.lesson_type_id == lesson_type_id
    ).first()
    if existing_lesson_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель уже имеет этот тип занятия'
        )

    teacher_lesson_type = TeacherLessonType(
        teacher_id=teacher_id,
        lesson_type_id=lesson_type_id
    )
    db.add(teacher_lesson_type)

    db.commit()
    db.refresh(teacher)

    return teacher


@router.delete('/lesson-types/{teacher_id}/{lesson_type_id}')
async def delete_teacher_lesson_type(
        teacher_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        response: Response,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    check_teacher(teacher, current_user)

    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип занятия не найден'
        )

    existing_lesson_type = db.query(TeacherLessonType).where(
        TeacherLessonType.teacher_id == teacher_id,
        TeacherLessonType.lesson_type_id == lesson_type_id
    ).first()
    if not existing_lesson_type:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 'Преподаватель не связан с этим типом занятия'

    db.delete(existing_lesson_type)
    db.commit()

    return 'Тип занятия преподавателя удалён успешно'


@router.post('/groups/{teacher_id}/{group_id}', response_model=TeacherFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_teacher_group(
        teacher_id: uuid.UUID,
        group_id: uuid.UUID,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
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

    existing_group = db.query(TeacherGroup).where(
        TeacherGroup.teacher_id == teacher_id,
        TeacherGroup.group_id == group_id
    ).first()
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель уже связан с этой группой'
        )

    teacher_group = TeacherGroup(
        teacher_id=teacher_id,
        group_id=group_id
    )
    db.add(teacher_group)

    db.commit()
    db.refresh(teacher)

    return teacher


@router.delete('/groups/{teacher_id}/{group_id}')
async def delete_teacher_group(
        teacher_id: uuid.UUID,
        group_id: uuid.UUID,
        response: Response,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )

    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    existing_group = db.query(TeacherGroup).where(
        TeacherGroup.teacher_id == teacher_id,
        TeacherGroup.group_id == group_id
    ).first()
    if not existing_group:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 'Преподаватель не связан с этой группой'

    db.query(TeacherLesson).where(
        TeacherLesson.teacher_id == teacher_id,
        db.query(Lesson).where(
            Lesson.id == TeacherLesson.lesson_id,
            Lesson.group_id == group_id,
            Lesson.start_time >= datetime.now(TIMEZONE)
        ).exists()
    ).delete()

    db.delete(existing_group)
    db.commit()

    return 'Преподаватель успешно удалён из группы'


@router.post('/lessons/{teacher_id}/{lesson_id}', response_model=LessonFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_teacher_lesson(
        teacher_id: uuid.UUID,
        lesson_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    check_teacher(teacher, current_user)

    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )
    if lesson.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Занятие отменено'
        )

    existing_teacher_lesson = db.query(TeacherLesson).where(
        TeacherLesson.teacher_id == teacher_id,
        TeacherLesson.lesson_id == lesson_id
    ).first()
    if existing_teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель уже связан с этим занятием'
        )

    parallel_teacher_lesson = get_teacher_parallel_lesson(teacher_id, lesson.start_time, lesson.finish_time, db)
    if parallel_teacher_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Преподаватель уже связан с пересекающимся по времени занятием'
        )

    teacher_lesson = TeacherLesson(
        teacher_id=teacher_id,
        lesson_id=lesson_id
    )
    db.add(teacher_lesson)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.delete('/lessons/{teacher_id}/{lesson_id}')
async def delete_teacher_lesson(
        teacher_id: uuid.UUID,
        lesson_id: uuid.UUID,
        response: Response,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == teacher_id).first()
    check_teacher(teacher, current_user)

    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )
    if lesson.start_time <= datetime.now(TIMEZONE) and not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Занятие уже началось'
        )

    existing_lesson = db.query(TeacherLesson).where(
        TeacherLesson.teacher_id == teacher_id,
        TeacherLesson.lesson_id == lesson_id
    ).first()
    if not existing_lesson:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 'Преподаватель не связан с этим занятием'

    if not lesson.group_id:
        db.query(LessonSubscription).where(
            LessonSubscription.lesson_id == lesson_id
        ).update(
            {LessonSubscription.cancelled: True}
        )

        lesson.terminated = True

    db.delete(existing_lesson)
    db.commit()

    return 'Преподаватель успешно удалён из занятия'
