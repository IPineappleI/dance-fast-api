from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin
from app.database import get_db
from app.routers.auth import create_user, patch_user
from app.models import User, Admin
from app.schemas.admin import *

router = APIRouter(
    prefix='/admins',
    tags=['admins']
)


@router.post('/', response_model=AdminInfo, status_code=status.HTTP_201_CREATED)
async def create_admin(
        admin_data: AdminCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    user = create_user(admin_data, db)

    admin = Admin(
        user_id=user.id
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def check_order_by(order_by: str) -> str:
    assert order_by in ['created_at'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=AdminPage)
async def search_admins(
        filters: AdminFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admins = db.query(Admin)

    if filters.terminated is not None:
        admins = admins.join(User).where(User.terminated == filters.terminated)

    return AdminPage(
        admins=admins.order_by(
            text('admins.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=admins.count()
    )


@router.post('/search/full-info', response_model=AdminFullInfoPage)
async def search_admins_full_info(
        filters: AdminFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admins = db.query(Admin)

    if filters.terminated is not None:
        admins = admins.join(User).where(User.terminated == filters.terminated)

    return AdminFullInfoPage(
        admins=admins.order_by(
            text('admins.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=admins.count()
    )


@router.get('/{admin_id}', response_model=AdminInfo)
async def get_admin_by_id(
        admin_id: uuid.UUID,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admin = db.query(Admin).where(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Администратор не найден'
        )
    return admin


@router.get('/full-info/{admin_id}', response_model=AdminFullInfo)
async def get_admin_full_info_by_id(
        admin_id: uuid.UUID,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admin = db.query(Admin).where(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Администратор не найден'
        )
    return admin


@router.patch('/{admin_id}', response_model=AdminFullInfo)
async def patch_admin(
        admin_id: uuid.UUID,
        admin_data: AdminUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admin = db.query(Admin).where(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Администратор не найден'
        )

    patch_user(admin.user_id, admin_data, db)

    db.refresh(admin)

    return admin
