import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.auth.jwt import get_current_admin
from app.database import get_db
from app import models, schemas
from app.routers.users import create_user, patch_user


router = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Администратор не найден"}}
)


@router.post("/", response_model=schemas.AdminInfo, status_code=status.HTTP_201_CREATED)
async def create_admin(
        admin_data: schemas.AdminCreate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    user = create_user(admin_data, db)

    admin = models.Admin(
        user_id=user.id
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


@router.get("/", response_model=List[schemas.AdminInfo])
async def get_admins(
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admins = db.query(models.Admin).offset(skip).limit(limit).all()
    return admins


@router.get("/full-info", response_model=List[schemas.AdminFullInfo])
async def get_admins_full_info(
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admins = db.query(models.Admin).offset(skip).limit(limit).all()
    return admins


@router.get("/{admin_id}", response_model=schemas.AdminInfo)
async def get_admin_by_id(
        admin_id: uuid.UUID,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )
    return admin


@router.get("/full-info/{admin_id}", response_model=schemas.AdminFullInfo)
async def get_admin_full_info_by_id(
        admin_id: uuid.UUID,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )
    return admin


@router.patch("/{admin_id}", response_model=schemas.AdminFullInfo, status_code=status.HTTP_200_OK)
async def patch_admin(
        admin_id: uuid.UUID,
        admin_data: schemas.AdminUpdate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )

    patch_user(admin.user_id, admin_data, db)

    db.refresh(admin)

    return admin
