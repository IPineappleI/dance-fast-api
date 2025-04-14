from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db

import uuid

router = APIRouter(
    prefix="/eventTypes",
    tags=["event types"],
    responses={404: {"description": "Тип мероприятия не найден"}}
    # dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=schemas.EventTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_event_type(
        event_type_data: schemas.EventTypeBase,
        db: Session = Depends(get_db)
):
    event_type = models.EventType(
        name=event_type_data.name,
        description=event_type_data.description,
        created_at=datetime.now(timezone.utc)
    )

    db.add(event_type)
    db.commit()
    db.refresh(event_type)

    return event_type


@router.get("/", response_model=List[schemas.EventTypeInfo])
async def get_all_event_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    event_types = db.query(models.EventType).offset(skip).limit(limit).all()
    return event_types


@router.get("/{event_type_id}", response_model=schemas.EventTypeInfo)
async def get_event_type_by_id(event_type_id: uuid.UUID, db: Session = Depends(get_db)):
    event_type = db.query(models.EventType).filter(models.EventType.id == event_type_id).first()
    if event_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип мероприятия не найден"
        )
    return event_type


@router.patch("/{event_type_id}", response_model=schemas.EventTypeInfo, status_code=status.HTTP_200_OK)
async def patch_event_type(
        event_type_id: uuid.UUID,
        event_type_data: schemas.EventTypeUpdate,
        db: Session = Depends(get_db)
):
    event_type = db.query(models.EventType).filter(models.EventType.id == event_type_id).first()
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип мероприятия не найдено"
        )

    for field, value in event_type_data.model_dump(exclude_unset=True).items():
        setattr(event_type, field, value)

    db.commit()
    db.refresh(event_type)
    return event_type
