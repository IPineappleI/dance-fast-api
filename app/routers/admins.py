import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin

router = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Администратор не найден"}}
)


@router.post("/", response_model=schemas.AdminInfo, status_code=status.HTTP_201_CREATED)
async def create_admin(
        admin_data: schemas.AdminBase,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == admin_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователя с идентификатором {admin_data.user_id} не существует",
        )

    admin = models.Admin(
        user_id=admin_data.user_id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


@router.get("/", response_model=List[schemas.AdminInfo])
async def get_all_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    admins = db.query(models.Admin).offset(skip).limit(limit).all()
    return admins


@router.get("/full-info", response_model=List[schemas.AdminFullInfo])
async def get_all_admins_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    admins = db.query(models.Admin).offset(skip).limit(limit).all()
    return admins


@router.get("/{admin_id}", response_model=schemas.AdminInfo)
async def get_admin_by_id(admin_id: uuid.UUID, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )
    return admin


@router.get("/full-info/{admin_id}", response_model=schemas.AdminFullInfo)
async def get_admin_full_info_by_id(admin_id: uuid.UUID, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )

    return admin


@router.patch("/{admin_id}", response_model=schemas.AdminInfo, status_code=status.HTTP_200_OK)
async def patch_admin(admin_id: uuid.UUID, admin_data: schemas.AdminUpdate, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )

    if admin_data.user_id:
        user = db.query(models.User).filter(models.User.id == admin_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

    for field, value in admin_data.model_dump(exclude_unset=True).items():
        setattr(admin, field, value)

    db.commit()
    db.refresh(admin)
    return admin


@router.delete("/{admin_id}")
async def delete_admin_by_id(admin_id: uuid.UUID, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Администратор не найден"
        )

    db.delete(admin)
    db.commit()

    return "Администратор успешно удален"
