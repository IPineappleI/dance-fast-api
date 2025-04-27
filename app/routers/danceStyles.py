from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Annotated

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.models import User, Admin, DanceStyle
from app.schemas.danceStyle import *

import uuid

router = APIRouter(
    prefix='/danceStyles',
    tags=['dance styles']
)


@router.post('/', response_model=DanceStyleInfo, status_code=status.HTTP_201_CREATED)
async def create_dance_style(
        dance_style_data: DanceStyleCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    dance_style = DanceStyle(
        name=dance_style_data.name,
        description=dance_style_data.description,
        photo_url=dance_style_data.photo_url
    )

    db.add(dance_style)
    db.commit()
    db.refresh(dance_style)

    return dance_style


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=DanceStylePage)
async def search_dance_styles(
        filters: DanceStyleFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    dance_styles = db.query(DanceStyle)

    if filters.terminated is not None:
        dance_styles = dance_styles.where(DanceStyle.terminated == filters.terminated)

    return DanceStylePage(
        dance_styles=dance_styles.order_by(
            text('dance_styles.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=dance_styles.count()
    )


@router.get('/{dance_style_id}', response_model=DanceStyleInfo)
async def get_dance_style_by_id(
        dance_style_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    dance_style = db.query(DanceStyle).where(DanceStyle.id == dance_style_id).first()
    if not dance_style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стиль танца не найден'
        )
    return dance_style


@router.patch('/{dance_style_id}', response_model=DanceStyleInfo)
async def patch_dance_style(
        dance_style_id: uuid.UUID,
        dance_style_data: DanceStyleUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    dance_style = db.query(DanceStyle).where(DanceStyle.id == dance_style_id).first()
    if not dance_style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стиль танца не найден'
        )

    for field, value in dance_style_data.model_dump(exclude_unset=True).items():
        setattr(dance_style, field, value)

    db.commit()
    db.refresh(dance_style)

    return dance_style
