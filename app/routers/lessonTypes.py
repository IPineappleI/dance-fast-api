from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.models import User, Admin, LessonType, DanceStyle
from app.schemas.lessonType import *

import uuid

router = APIRouter(
    prefix='/lessonTypes',
    tags=['lesson types']
)


def check_lesson_type_data(lesson_type_data, db: Session, existing_lesson_type=None):
    if lesson_type_data.dance_style_id:
        dance_style = db.query(DanceStyle).where(
            DanceStyle.id == lesson_type_data.dance_style_id
        ).first()
        if not dance_style:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Стиль танца не найден'
            )
        if dance_style.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Стиль танца не активен'
            )

    if lesson_type_data.dance_style_id or lesson_type_data.is_group is not None:
        dance_style_id = lesson_type_data.dance_style_id if lesson_type_data.dance_style_id \
            else existing_lesson_type.dance_style_id

        is_group = lesson_type_data.is_group if lesson_type_data.is_group is not None \
            else existing_lesson_type.is_group

        lesson_type_check = db.query(LessonType).where(
            LessonType.dance_style_id == dance_style_id,
            LessonType.is_group == is_group
        ).first()

        if lesson_type_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Такой тип занятия уже существует'
            )


@router.post('/', response_model=LessonTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_lesson_type(
        lesson_type_data: LessonTypeCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    check_lesson_type_data(lesson_type_data, db)

    lesson_type = LessonType(
        dance_style_id=lesson_type_data.dance_style_id,
        is_group=lesson_type_data.is_group
    )

    db.add(lesson_type)
    db.commit()
    db.refresh(lesson_type)

    return lesson_type


def apply_filters_to_lesson_types(lesson_types, filters):
    if filters.dance_style_ids:
        lesson_types = lesson_types.where(LessonType.dance_style_id.in_(filters.dance_style_ids))

    if filters.is_group is not None:
        lesson_types = lesson_types.where(LessonType.is_group == filters.is_group)
    if filters.terminated is not None:
        lesson_types = lesson_types.where(LessonType.terminated == filters.terminated)

    return lesson_types


def check_order_by(order_by: str) -> str:
    assert order_by in ['is_group', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=LessonTypePage)
async def search_lesson_types(
        filters: LessonTypeFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson_types = db.query(LessonType)
    lesson_types = apply_filters_to_lesson_types(lesson_types, filters)
    return LessonTypePage(
        lesson_types=lesson_types.order_by(
            text('lesson_types.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lesson_types.count()
    )


@router.post('/search/full-info', response_model=LessonTypeFullInfoPage)
async def search_lesson_types_full_info(
        filters: LessonTypeFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson_types = db.query(LessonType)
    lesson_types = apply_filters_to_lesson_types(lesson_types, filters)
    return LessonTypeFullInfoPage(
        lesson_types=lesson_types.order_by(
            text('lesson_types.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=lesson_types.count()
    )


@router.get('/{lesson_type_id}', response_model=LessonTypeInfo)
async def get_lesson_type_by_id(
        lesson_type_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип занятия не найден'
        )
    return lesson_type


@router.get('/full-info/{lesson_type_id}', response_model=LessonTypeFullInfo)
async def get_lesson_type_full_info_by_id(
        lesson_type_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип занятия не найден'
        )
    return lesson_type


@router.patch('/{lesson_type_id}', response_model=LessonTypeFullInfo)
async def patch_lesson_type(
        lesson_type_id: uuid.UUID,
        lesson_type_data: LessonTypeUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип занятия не найден'
        )

    check_lesson_type_data(lesson_type_data, db, lesson_type)

    for field, value in lesson_type_data.model_dump(exclude_unset=True).items():
        setattr(lesson_type, field, value)

    db.commit()
    db.refresh(lesson_type)

    return lesson_type
