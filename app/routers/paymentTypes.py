from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db

import uuid


router = APIRouter(
    prefix="/paymentTypes",
    tags=["payment types"],
    responses={404: {"description": "Тип платежа не найден"}}
)


@router.post("/", response_model=schemas.PaymentTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_payment_type(
        payment_type_data: schemas.PaymentTypeBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    payment_type = models.PaymentType(
        name=payment_type_data.name
    )

    db.add(payment_type)
    db.commit()
    db.refresh(payment_type)

    return payment_type


@router.get("/", response_model=List[schemas.PaymentTypeInfo])
async def get_payment_types(
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    payment_types = db.query(models.PaymentType).offset(skip).limit(limit).all()
    return payment_types


@router.get("/active", response_model=List[schemas.PaymentTypeInfo])
async def get_active_payment_types(
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment_types = db.query(models.PaymentType).filter(
        models.PaymentType.terminated == False
    ).offset(skip).limit(limit).all()

    return payment_types


@router.get("/{payment_type_id}", response_model=schemas.PaymentTypeInfo)
async def get_payment_type_by_id(
        payment_type_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment_type = db.query(models.PaymentType).filter(models.PaymentType.id == payment_type_id).first()
    if payment_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип платежа не найден"
        )
    return payment_type


@router.patch("/{payment_type_id}", response_model=schemas.PaymentTypeInfo, status_code=status.HTTP_200_OK)
async def patch_payment_type(
        payment_type_id: uuid.UUID,
        payment_type_data: schemas.PaymentTypeUpdate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    payment_type = db.query(models.PaymentType).filter(models.PaymentType.id == payment_type_id).first()
    if not payment_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип платежа не найден"
        )

    for field, value in payment_type_data.model_dump(exclude_unset=True).items():
        setattr(payment_type, field, value)

    db.commit()
    db.refresh(payment_type)

    return payment_type
