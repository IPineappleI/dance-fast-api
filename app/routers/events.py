from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db, TIMEZONE
from app.models import User, Admin, Event, EventType
from app.schemas.event import *
from app.email import send_new_event_email, send_event_rescheduled_email, send_event_cancelled_email

import uuid

router = APIRouter(
    prefix='/events',
    tags=['events']
)


@router.post('/', response_model=EventInfo, status_code=status.HTTP_201_CREATED)
async def create_event(
        event_data: EventCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    event_data.start_time = event_data.start_time.astimezone(TIMEZONE)
    if event_data.start_time <= datetime.now(TIMEZONE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Мероприятие должно начинаться в будущем'
        )

    event_type = db.query(EventType).where(EventType.id == event_data.event_type_id).first()
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип мероприятия не найден'
        )
    if event_type.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тип мероприятия не активен'
        )

    event = Event(
        event_type_id=event_data.event_type_id,
        name=event_data.name,
        description=event_data.description,
        start_time=event_data.start_time,
        photo_url=event_data.photo_url
    )

    db.add(event)
    db.commit()

    await send_new_event_email(event, db)

    db.refresh(event)

    return event


def apply_filters_to_events(events, filters):
    if filters.date_from:
        filters.date_from = filters.date_from.astimezone(TIMEZONE)
        events = events.where(Event.start_time >= filters.date_from)
    if filters.date_to:
        filters.date_to = filters.date_to.astimezone(TIMEZONE)
        events = events.where(Event.start_time <= filters.date_to)

    if filters.search_string:
        events = events.where(Event.name.ilike(f'%{filters.search_string}%'))

    if filters.event_type_ids:
        events = events.where(Event.event_type_id.in_(filters.event_type_ids))

    if filters.terminated is not None:
        events = events.where(Event.terminated == filters.terminated)

    return events


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'start_time', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=EventPage)
async def search_events(
        filters: EventFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    events = db.query(Event)
    events = apply_filters_to_events(events, filters)
    return EventPage(
        events=events.order_by(
            text('events.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=events.count()
    )


@router.post('/search/full-info', response_model=EventFullInfoPage)
async def search_events_full_info(
        filters: EventFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    events = db.query(Event)
    events = apply_filters_to_events(events, filters)
    return EventFullInfoPage(
        events=events.order_by(
            text('events.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=events.count()
    )


@router.get('/{event_id}', response_model=EventInfo)
async def get_event_by_id(
        event_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event = db.query(Event).where(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Мероприятие не найдено'
        )
    return event


@router.get('/full-info/{event_id}', response_model=EventFullInfo)
async def get_event_full_info_by_id(
        event_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event = db.query(Event).where(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Мероприятие не найдено'
        )
    return event


@router.patch('/{event_id}', response_model=EventFullInfo)
async def patch_event(
        event_id: uuid.UUID,
        event_data: EventUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    event = db.query(Event).where(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Мероприятие не найдено'
        )

    if event_data.start_time:
        event_data.start_time = event_data.start_time.astimezone(TIMEZONE)

    if event_data.event_type_id:
        event_type = db.query(EventType).where(EventType.id == event_data.event_type_id).first()
        if not event_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Тип мероприятия не найден'
            )
        if event_type.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Тип мероприятия не активен'
            )

    old_terminated = event.terminated
    old_start_time = event.start_time

    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()

    if not old_terminated:
        if event.terminated:
            await send_event_cancelled_email(event, db)
        elif event.start_time != old_start_time:
            await send_event_rescheduled_email(event, db)
    elif not event.terminated:
        await send_event_rescheduled_email(event, db)

    db.refresh(event)

    return event
