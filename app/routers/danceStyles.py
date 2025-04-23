from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db

import uuid


router = APIRouter(
    prefix="/danceStyles",
    tags=["dance styles"],
    responses={404: {"description": "Стиль танца не найден"}}
)


@router.post("/", response_model=schemas.DanceStyleInfo, status_code=status.HTTP_201_CREATED)
async def create_dance_style(
        dance_style_data: schemas.DanceStyleBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    dance_style = models.DanceStyle(
        name=dance_style_data.name,
        description=dance_style_data.description,
        photo_url=dance_style_data.photo_url
    )

    db.add(dance_style)
    db.commit()
    db.refresh(dance_style)

    return dance_style


@router.get("/", response_model=List[schemas.DanceStyleInfo])
async def get_dance_styles(
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    dance_styles = db.query(models.DanceStyle).offset(skip).limit(limit).all()
    return dance_styles


@router.get("/active", response_model=List[schemas.DanceStyleInfo])
async def get_active_dance_styles(
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    dance_styles = db.query(models.DanceStyle).filter(
        models.DanceStyle.terminated != True
    ).offset(skip).limit(limit).all()

    return dance_styles


@router.get("/{dance_style_id}", response_model=schemas.DanceStyleInfo)
async def get_dance_style_by_id(
        dance_style_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    dance_style = db.query(models.DanceStyle).filter(models.DanceStyle.id == dance_style_id).first()
    if not dance_style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стиль танца не найден"
        )
    return dance_style


@router.patch("/{dance_style_id}", response_model=schemas.DanceStyleInfo, status_code=status.HTTP_200_OK)
async def patch_dance_style(
        dance_style_id: uuid.UUID,
        dance_style_data: schemas.DanceStyleUpdate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    dance_style = db.query(models.DanceStyle).filter(models.DanceStyle.id == dance_style_id).first()
    if not dance_style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стиль танца не найден"
        )

    for field, value in dance_style_data.model_dump(exclude_unset=True).items():
        setattr(dance_style, field, value)

    db.commit()
    db.refresh(dance_style)

    return dance_style
