import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin

router = APIRouter(
    prefix="/levels",
    tags=["levels"],
    responses={404: {"description": "Уровень не найден"}}
)


@router.post("/", response_model=schemas.LevelInfo, status_code=status.HTTP_201_CREATED)
async def create_level(
        level_data: schemas.LevelBase,
        db: Session = Depends(get_db)
):
    level = models.Level(
        name=level_data.name,
        description=level_data.description,
        created_at=datetime.now(timezone.utc)
    )

    db.add(level)
    db.commit()
    db.refresh(level)

    return level


@router.get("/", response_model=List[schemas.LevelInfo])
async def get_all_levels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    levels = db.query(models.Level).offset(skip).limit(limit).all()
    return levels


@router.get("/{level_id}", response_model=schemas.LevelInfo)
async def get_level_by_id(level_id: uuid.UUID, db: Session = Depends(get_db)):
    level = db.query(models.Level).filter(models.Level.id == level_id).first()
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уровень не найден"
        )
    return level


@router.patch("/{level_id}", response_model=schemas.LevelInfo, status_code=status.HTTP_200_OK)
async def patch_level(level_id: uuid.UUID, level_data: schemas.LevelUpdate, db: Session = Depends(get_db)):
    level = db.query(models.Level).filter(models.Level.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уровень не найден"
        )

    for field, value in level_data.model_dump(exclude_unset=True).items():
        setattr(level, field, value)

    db.commit()
    db.refresh(level)

    return level
