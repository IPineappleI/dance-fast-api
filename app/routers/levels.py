from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.models import User, Admin, Level
from app.schemas.level import *

router = APIRouter(
    prefix='/levels',
    tags=['levels']
)


@router.post('/', response_model=LevelInfo, status_code=status.HTTP_201_CREATED)
async def create_level(
        level_data: LevelCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    level = Level(
        name=level_data.name,
        description=level_data.description
    )

    db.add(level)
    db.commit()
    db.refresh(level)

    return level


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=LevelPage)
async def search_levels(
        filters: LevelFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        db: Session = Depends(get_db)
):
    levels = db.query(Level)

    if filters.terminated is not None:
        levels = levels.where(Level.terminated == filters.terminated)

    return LevelPage(
        levels=levels.order_by(
            text('levels.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=levels.count()
    )


@router.get('/{level_id}', response_model=LevelInfo)
async def get_level_by_id(
        level_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    level = db.query(Level).where(Level.id == level_id).first()
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Уровень подготовки не найден'
        )
    return level


@router.patch('/{level_id}', response_model=LevelInfo)
async def patch_level(
        level_id: uuid.UUID,
        level_data: LevelUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    level = db.query(Level).where(Level.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Уровень подготовки не найден'
        )

    for field, value in level_data.model_dump(exclude_unset=True).items():
        setattr(level, field, value)

    db.commit()
    db.refresh(level)

    return level
