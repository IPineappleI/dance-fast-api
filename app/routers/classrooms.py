from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from pytz import timezone
from sqlalchemy import exists, and_, or_, text
from sqlalchemy.orm import Session
from typing import Annotated

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.models import Classroom, User, Admin, Lesson
from app.schemas.classroom import *

import uuid

router = APIRouter(
    prefix='/classrooms',
    tags=['classrooms']
)


@router.post('/', response_model=ClassroomInfo, status_code=status.HTTP_201_CREATED)
async def create_classroom(
        classroom_data: ClassroomCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    classroom = Classroom(
        name=classroom_data.name,
        description=classroom_data.description
    )

    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return classroom


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=ClassroomPage)
async def search_classrooms(
        filters: ClassroomFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    classrooms = db.query(Classroom)

    if filters.terminated is not None:
        classrooms = classrooms.where(Classroom.terminated == filters.terminated)

    return ClassroomPage(
        classrooms=classrooms.order_by(
            text('classrooms.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=classrooms.count()
    )


@router.post('/search/available', response_model=ClassroomPage)
async def search_available_classrooms(
        filters: ClassroomAvailableFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    filters.date_from = filters.date_from.astimezone(timezone('Europe/Moscow'))
    filters.date_to = filters.date_to.astimezone(timezone('Europe/Moscow'))
    if filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время начала поиска не может быть больше времени конца поиска'
        )
    if filters.date_from < datetime.now(timezone('Europe/Moscow')):
        return ClassroomPage(classrooms=[], total=0)

    classrooms = db.query(Classroom).where(Classroom.terminated == False).where(~exists(Lesson).where(
        Lesson.classroom_id == Classroom.id,
        Lesson.terminated == False,
        or_(
            filters.are_neighbours_allowed == False,
            Lesson.are_neighbours_allowed == False
        ),
        or_(
            and_(filters.date_from >= Lesson.start_time, filters.date_from < Lesson.finish_time),
            and_(filters.date_to > Lesson.start_time, filters.date_to <= Lesson.finish_time),
            and_(filters.date_from <= Lesson.start_time, filters.date_to >= Lesson.finish_time)
        )
    ))

    return ClassroomPage(
        classrooms=classrooms.order_by(
            text('classrooms.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=classrooms.count()
    )


@router.get('/{classroom_id}', response_model=ClassroomInfo)
async def get_classroom_by_id(
        classroom_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    classroom = db.query(Classroom).where(Classroom.id == classroom_id).first()
    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Зал не найден'
        )
    return classroom


@router.patch('/{classroom_id}', response_model=ClassroomInfo)
async def patch_classroom(
        classroom_id: uuid.UUID,
        classroom_data: ClassroomUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    classroom = db.query(Classroom).where(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Зал не найден'
        )

    for field, value in classroom_data.model_dump(exclude_unset=True).items():
        setattr(classroom, field, value)

    db.commit()
    db.refresh(classroom)
    return classroom
