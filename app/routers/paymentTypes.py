from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app.email import send_new_payment_type_email, send_payment_type_terminated_email
from app.models import User, Admin, PaymentType
from app.schemas.paymentType import *

import uuid

router = APIRouter(
    prefix='/paymentTypes',
    tags=['payment types']
)


@router.post('/', response_model=PaymentTypeInfo, status_code=status.HTTP_201_CREATED)
async def create_payment_type(
        payment_type_data: PaymentTypeCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    payment_type = PaymentType(
        name=payment_type_data.name
    )

    db.add(payment_type)
    db.commit()

    await send_new_payment_type_email(payment_type, db)

    db.refresh(payment_type)

    return payment_type


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'created_at', 'terminated'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=PaymentTypePage)
async def search_payment_types(
        filters: PaymentTypeFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment_types = db.query(PaymentType)

    if filters.terminated is not None:
        payment_types = payment_types.where(PaymentType.terminated == filters.terminated)

    return PaymentTypePage(
        payment_types=payment_types.order_by(
            text('payment_types.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=payment_types.count()
    )


@router.get('/{payment_type_id}', response_model=PaymentTypeInfo)
async def get_payment_type_by_id(
        payment_type_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment_type = db.query(PaymentType).where(PaymentType.id == payment_type_id).first()
    if payment_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип платежа не найден'
        )
    return payment_type


@router.patch('/{payment_type_id}', response_model=PaymentTypeInfo)
async def patch_payment_type(
        payment_type_id: uuid.UUID,
        payment_type_data: PaymentTypeUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    payment_type = db.query(PaymentType).where(PaymentType.id == payment_type_id).first()
    if not payment_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип платежа не найден'
        )

    old_terminated = payment_type.terminated

    for field, value in payment_type_data.model_dump(exclude_unset=True).items():
        setattr(payment_type, field, value)

    db.commit()

    if payment_type.terminated and not old_terminated:
        await send_payment_type_terminated_email(payment_type, db)
    elif not payment_type.terminated and old_terminated:
        await send_new_payment_type_email(payment_type, db)

    db.refresh(payment_type)

    return payment_type
