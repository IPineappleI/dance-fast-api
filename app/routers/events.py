from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, Query
from typing import List
from app import schemas, models
from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db

import uuid


router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Мероприятие не найдено"}}
)


@router.post("/", response_model=schemas.EventInfo, status_code=status.HTTP_201_CREATED)
async def create_event(
        event_data: schemas.EventBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if event_data.start_time <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мероприятие должно начинаться в будущем"
        )

    event_type = db.query(models.EventType).filter(models.EventType.id == event_data.event_type_id).first()
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип мероприятия не найден"
        )
    if event_type.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тип мероприятия не активен"
        )

    event = models.Event(
        event_type_id=event_data.event_type_id,
        name=event_data.name,
        description=event_data.description,
        start_time=event_data.start_time,
        photo_url=event_data.photo_url
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def apply_filters_to_events(events: Query, filters):
    if filters.date_from:
        events = events.filter(models.Event.start_time >= filters.date_from)
    if filters.date_to:
        events = events.filter(models.Event.start_time <= filters.date_to)

    if filters.search_string:
        events = events.filter(models.Event.name.ilike(f"%{filters.search_string}%"))

    if filters.event_type_ids:
        events = events.filter(models.Event.event_type_id.in_(filters.event_type_ids))

    if type(filters.terminated) is bool:
        events = events.filter(models.Event.terminated == filters.terminated)

    return events


@router.post("/search", response_model=List[schemas.EventInfo])
async def search_events(
        filters: schemas.EventSearch,
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    events = db.query(models.Event)
    events = apply_filters_to_events(events, filters)
    events = events.offset(skip).limit(limit).all()
    return events


@router.post("/search/full-info", response_model=List[schemas.EventFullInfo])
async def search_events_full_info(
        filters: schemas.EventSearch,
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    events = db.query(models.Event)
    events = apply_filters_to_events(events, filters)
    events = events.offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=schemas.EventInfo)
async def get_event_by_id(
        event_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )
    return event


@router.get("/full-info/{event_id}", response_model=schemas.EventFullInfo)
async def get_event_full_info_by_id(
        event_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )
    return event


@router.patch("/{event_id}", response_model=schemas.EventFullInfo, status_code=status.HTTP_200_OK)
async def patch_event(
        event_id: uuid.UUID,
        event_data: schemas.EventUpdate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )

    if event_data.start_time and event_data.start_time <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мероприятие должно начинаться в будущем"
        )

    if event_data.event_type_id:
        event_type = db.query(models.EventType).filter(models.EventType.id == event_data.event_type_id).first()
        if not event_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тип мероприятия не найден"
            )
        if event_type.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип мероприятия не активен"
            )

    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event
