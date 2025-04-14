import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Группа не найдена"}}
)


@router.post("/", response_model=schemas.GroupInfo, status_code=status.HTTP_201_CREATED)
async def create_group(
        group_data: schemas.GroupBase,
        db: Session = Depends(get_db)
):
    level = db.query(models.Level).filter(models.Level.id == group_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Уровня подготовки с идентификатором {group_data.level_id} не существует",
        )

    group = models.Group(
        name=group_data.name,
        description=group_data.description,
        max_capacity=group_data.max_capacity,
        level_id=group_data.level_id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return group


@router.get("/", response_model=List[schemas.GroupInfo])
async def get_all_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = db.query(models.Group).offset(skip).limit(limit).all()
    return groups


@router.get("/full-info", response_model=List[schemas.GroupFullInfo])
async def get_all_groups_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = db.query(models.Group).offset(skip).limit(limit).all()
    return groups


@router.get("/{group_id}", response_model=schemas.GroupInfo)
async def get_group_by_id(group_id: uuid.UUID, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    return group


@router.get("/full-info/{group_id}", response_model=schemas.GroupFullInfo)
async def get_group_full_info_by_id(group_id: uuid.UUID, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    return group


@router.patch("/{group_id}", response_model=schemas.GroupInfo, status_code=status.HTTP_200_OK)
async def patch_group(
        group_id: uuid.UUID, group_data: schemas.GroupUpdate,
        db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    if group_data.level_id:
        level = db.query(models.Level).filter(models.Level.id == group_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Уровень не найден",
            )

    for field, value in group_data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    return group
