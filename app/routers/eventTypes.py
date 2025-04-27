from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.models import User, Admin, EventType
from app.schemas.eventType import *

import uuid

router = APIRouter(
    prefix='/eventTypes',
    tags=['event types']
)


@router.post('/', response_model=EventTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_event_type(
        event_type_data: EventTypeCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    event_type = EventType(
        name=event_type_data.name,
        description=event_type_data.description
    )

    db.add(event_type)
    db.commit()
    db.refresh(event_type)

    return event_type


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=EventTypePage)
async def search_event_types(
        filters: EventTypeFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event_types = db.query(EventType)

    if filters.terminated is not None:
        event_types = event_types.where(EventType.terminated == filters.terminated)

    return EventTypePage(
        event_types=event_types.order_by(
            text('event_types.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=event_types.count()
    )


@router.get('/{event_type_id}', response_model=EventTypeInfo)
async def get_event_type_by_id(
        event_type_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event_type = db.query(EventType).where(EventType.id == event_type_id).first()
    if event_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип мероприятия не найден'
        )
    return event_type


@router.patch('/{event_type_id}', response_model=EventTypeInfo)
async def patch_event_type(
        event_type_id: uuid.UUID,
        event_type_data: EventTypeUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    event_type = db.query(EventType).where(EventType.id == event_type_id).first()
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип мероприятия не найден'
        )

    for field, value in event_type_data.model_dump(exclude_unset=True).items():
        setattr(event_type, field, value)

    db.commit()
    db.refresh(event_type)
    return event_type
