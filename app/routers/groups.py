from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db, TIMEZONE
from app.email import send_new_group_email
from app.models import User, Admin, Group, Level, Lesson, LessonType
from app.models.association import *
from app.routers.students import get_fitting_subscriptions
from app.schemas.group import *

router = APIRouter(
    prefix='/groups',
    tags=['groups']
)


@router.post('/', response_model=GroupInfo, status_code=status.HTTP_201_CREATED)
async def create_group(
        group_data: GroupCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if group_data.max_capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Количество мест в группе должно быть положительным'
        )

    level = db.query(Level).where(Level.id == group_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Уровень подготовки не найден'
        )
    if level.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Уровень подготовки не активен'
        )

    group = Group(
        name=group_data.name,
        description=group_data.description,
        max_capacity=group_data.max_capacity,
        level_id=group_data.level_id
    )

    db.add(group)
    db.commit()

    await send_new_group_email(group, db)

    db.refresh(group)

    return group


def apply_filters_to_groups(groups: Query, filters, db):
    if filters.has_teachers is not None:
        groups = groups.where(
            db.query(TeacherGroup).where(
                TeacherGroup.group_id == Group.id
            ).exists() == filters.has_teachers
        )
    if filters.teacher_ids:
        groups = groups.where(
            db.query(TeacherGroup).where(
                TeacherGroup.group_id == Group.id,
                TeacherGroup.teacher_id.in_(filters.teacher_ids)
            ).exists()
        )

    if filters.has_students is not None:
        groups = groups.where(
            db.query(StudentGroup).where(
                StudentGroup.group_id == Group.id
            ).exists() == filters.has_students
        )
    if filters.student_ids:
        groups = groups.where(
            db.query(StudentGroup).where(
                StudentGroup.group_id == Group.id,
                StudentGroup.student_id.in_(filters.student_ids)
            ).exists()
        )

    if filters.level_ids:
        groups = groups.where(Group.level_id.in_(filters.level_ids))

    if filters.dance_style_ids:
        groups = groups.where(
            db.query(Lesson).where(
                Lesson.group_id == Group.id
            ).join(LessonType).where(
                LessonType.dance_style_id.in_(filters.dance_style_ids)
            ).exists()
        )

    if filters.terminated is not None:
        groups = groups.where(Group.terminated == filters.terminated)

    return groups


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'max_capacity', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=GroupPage)
async def search_groups(
        filters: GroupFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    groups = db.query(Group)
    groups = apply_filters_to_groups(groups, filters, db)
    return GroupPage(
        groups=groups.order_by(
            text('groups.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=groups.count()
    )


@router.post('/search/full-info', response_model=GroupFullInfoPage)
async def search_groups_full_info(
        filters: GroupFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    groups = db.query(Group)
    groups = apply_filters_to_groups(groups, filters, db)
    return GroupFullInfoPage(
        groups=groups.order_by(
            text('groups.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=groups.count()
    )


@router.get('/{group_id}', response_model=GroupInfo)
async def get_group_by_id(
        group_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )
    return group


@router.get('/full-info/{group_id}', response_model=GroupWithSubscriptions)
async def get_group_full_info_by_id(
        group_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    if current_user.student and current_user.student not in group.students:
        group.fitting_subscriptions = get_fitting_subscriptions(current_user.student, group, db)

    return group


@router.patch('/{group_id}', response_model=GroupFullInfo)
async def patch_group(
        group_id: uuid.UUID,
        group_data: GroupUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )

    if group_data.max_capacity is not None and group_data.max_capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Количество мест в группе должно быть положительным'
        )

    if group_data.level_id:
        level = db.query(Level).where(Level.id == group_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Уровень подготовки не найден'
            )
        if level.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Уровень подготовки не активен'
            )

    if group_data.terminated:
        db.query(TeacherGroup).where(
            TeacherGroup.group_id == group_id
        ).delete()

        db.query(StudentGroup).where(
            StudentGroup.group_id == group_id
        ).delete()

        group_lessons = db.query(Lesson).where(
            Lesson.group_id == group_id,
            Lesson.start_time >= datetime.now(TIMEZONE)
        )
        group_lessons.update(
            {Lesson.terminated: True}
        )

        group_lesson_ids = [group_lesson.id for group_lesson in group_lessons.all()]

        db.query(TeacherLesson).where(
            TeacherLesson.lesson_id.in_(group_lesson_ids)
        ).delete()

        db.query(LessonSubscription).where(
            LessonSubscription.lesson_id.in_(group_lesson_ids)
        ).update(
            {LessonSubscription.cancelled: True}
        )

    for field, value in group_data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    return group
