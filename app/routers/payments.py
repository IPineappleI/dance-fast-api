from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.models import User, Admin, Payment, PaymentType, Subscription
from app.schemas.payment import *

import uuid

router = APIRouter(
    prefix='/payments',
    tags=['payments']
)


@router.post('/', response_model=PaymentInfo, status_code=status.HTTP_201_CREATED)
async def create_payment(
        payment_data: PaymentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment_type = db.query(PaymentType).where(PaymentType.id == payment_data.payment_type_id).first()
    if not payment_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип платежа не найден'
        )
    if payment_type.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тип платежа не активен'
        )

    payment = Payment(
        payment_type_id=payment_data.payment_type_id,
        details=payment_data.details
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def apply_filters_to_payments(payments, filters):
    if filters.payment_type_ids:
        payments = payments.where(Payment.payment_type_id.in_(filters.payment_type_ids))

    if filters.student_id:
        payments = payments.join(Subscription).where(Subscription.student_id == filters.student_id)

    if filters.terminated is not None:
        payments = payments.where(Payment.terminated == filters.terminated)

    return payments


def check_order_by(order_by: str) -> str:
    assert order_by in ['details', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=PaymentPage)
async def search_payments(
        filters: PaymentFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payments = db.query(Payment)
    payments = apply_filters_to_payments(payments, filters)
    return PaymentPage(
        payments=payments.order_by(
            text('payments.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=payments.count()
    )


@router.post('/search/full-info', response_model=PaymentFullInfoPage)
async def search_payments_full_info(
        filters: PaymentFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payments = db.query(Payment)
    payments = apply_filters_to_payments(payments, filters)
    return PaymentFullInfoPage(
        payments=payments.order_by(
            text('payments.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=payments.count()
    )


@router.get('/{payment_id}', response_model=PaymentInfo)
async def get_payment_by_id(
        payment_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment = db.query(Payment).where(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Платёж не найден'
        )
    return payment


@router.get('/full-info/{payment_id}', response_model=PaymentFullInfo)
async def get_payment_full_info_by_id(
        payment_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment = db.query(Payment).where(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Платёж не найден'
        )
    return payment


@router.patch('/{payment_id}', response_model=PaymentFullInfo)
async def patch_payment(
        payment_id: uuid.UUID,
        payment_data: PaymentUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    payment = db.query(Payment).where(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Платёж не найден'
        )

    if payment_data.payment_type_id:
        payment_type = db.query(PaymentType).where(
            PaymentType.id == payment_data.payment_type_id
        ).first()
        if not payment_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Тип платежа не найден'
            )
        if payment_type.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Тип платежа не активен'
            )

    for field, value in payment_data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return payment
