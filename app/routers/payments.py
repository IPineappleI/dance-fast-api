from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db

import uuid

from app.schemas.payment import PaymentInfoWithType

from app.schemas.paymentType import PaymentTypeInfo

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Платеж не найден"}}
    # dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=schemas.PaymentInfo, status_code=status.HTTP_201_CREATED)
async def create_payment(
        payment_data: schemas.PaymentBase,
        db: Session = Depends(get_db)
):
    payment_type_id = db.query(models.PaymentType).filter(models.PaymentType.id == payment_data.payment_type_id).first()
    if not payment_type_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Тип платежа с идентификатором {payment_data.payment_type_id} не найден",
        )

    payment = models.Payment(
        payment_type_id=payment_data.payment_type_id,
        details=payment_data.details,
        created_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.get("/", response_model=List[schemas.PaymentInfo])
async def get_all_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).offset(skip).limit(limit).all()
    return payments


@router.get("/withType", response_model=List[schemas.PaymentInfoWithType])
async def get_all_payments_with_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=schemas.PaymentInfo)
async def get_payment_by_id(payment_id: uuid.UUID, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )
    return payment


@router.get("/withType/{payment_id}", response_model=schemas.PaymentInfoWithType)
async def get_payment_with_type_by_id(payment_id: uuid.UUID, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )

    payment_type = db.query(models.PaymentType).filter(models.PaymentType.id == payment.payment_type_id).first()
    if payment_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип платежа не найден"
        )

    return payment


@router.patch("/{payment_id}", response_model=schemas.PaymentInfo, status_code=status.HTTP_200_OK)
async def patch_payment(payment_id: uuid.UUID, payment_data: schemas.PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )

    if payment_data.payment_type_id:
        payment_type = db.query(models.PaymentType).filter(
            models.PaymentType.id == payment_data.payment_type_id).first()
        if not payment_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип платежа не найден",
            )

    for field, value in payment_data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return payment
