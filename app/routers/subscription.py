from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app import models, schemas
from app.auth.jwt import get_current_active_user, get_current_admin
from app.auth.password import get_password_hash

import uuid

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    responses={404: {"description": "Подписка не найдена"}}
)


@router.post("/", response_model=schemas.SubscriptionInfo, status_code=status.HTTP_201_CREATED)
async def create_subscription(
        subscription_data: schemas.SubscriptionBase,
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_data.subscription_template_id).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Шаблон подписки с идентификатором {subscription_data.subscription_template_id} не найден",
        )
    if subscription_template.active == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Шаблон подписки не активен"
        )
    if subscription_template.expiration_date <= datetime.now(timezone.utc):
        print(subscription_template.expiration_date)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Шаблон подписки просрочен"
        )
    student = db.query(models.Student).filter(models.Student.id == subscription_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Студент не найден"
        )
    payment = db.query(models.Payment).filter(models.Payment.id == subscription_data.payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Платеж не найден"
        )

    if subscription_data.expiration_date <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата окончания подписки просрочена"
        )

    subscription = models.Subscription(
        student_id=student.id,
        subscription_template_id=subscription_template.id,
        expiration_date=subscription_data.expiration_date,
        payment_id=payment.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.get("/", response_model=List[schemas.SubscriptionInfo])
async def get_all_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).offset(skip).limit(limit).all()
    return subscriptions


@router.get("/full-info", response_model=List[schemas.SubscriptionFullInfo])
async def get_all_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).offset(skip).limit(limit).all()

    subscriptions_with_templates = []

    for subscription in subscriptions:
        subscription_template = db.query(models.SubscriptionTemplate).filter(
            models.SubscriptionTemplate.id == subscription.subscription_template_id).first()

        subscription_with_template = schemas.SubscriptionFullInfo(
            id=subscription.id,
            student_id=subscription.student_id,
            subscription_template_id=subscription.subscription_template_id,
            expiration_date=subscription.expiration_date,
            payment_id=subscription.payment_id,
            subscription_template=schemas.SubscriptionTemplateInfo(
                id=subscription_template.id,
                name=subscription_template.name,
                description=subscription_template.description,
                lesson_count=subscription_template.lesson_count,
                expiration_date=subscription_template.expiration_date,
                expiration_day_count=subscription_template.expiration_day_count,
                price=subscription_template.price,
                active=subscription_template.active
            )
        )

        subscriptions_with_templates.append(subscription_with_template)

    return subscriptions_with_templates


@router.get("/{subscription_id}", response_model=schemas.SubscriptionInfo)
async def get_subscription_by_id(subscription_id: uuid.UUID, db: Session = Depends(get_db)):
    db_subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if db_subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )
    return db_subscription


@router.get("/full-info/{subscription_id}", response_model=schemas.SubscriptionFullInfo)
async def get_subscription_with_template_by_id(subscription_id: uuid.UUID, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription.subscription_template_id).first()
    if subscription_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон подписки не найден"
        )

    return schemas.SubscriptionFullInfo(
        id=subscription.id,
        student_id=subscription.student_id,
        subscription_template_id=subscription.subscription_template_id,
        expiration_date=subscription.expiration_date,
        payment_id=subscription.payment_id,
        subscription_template=schemas.SubscriptionTemplateInfo(
            id=subscription_template.id,
            name=subscription_template.name,
            description=subscription_template.description,
            lesson_count=subscription_template.lesson_count,
            expiration_date=subscription_template.expiration_date,
            expiration_day_count=subscription_template.expiration_day_count,
            price=subscription_template.price,
            active=subscription_template.active
        )
    )


@router.patch("/{subscription_id}", response_model=schemas.SubscriptionInfo, status_code=status.HTTP_200_OK)
async def patch_subscription(
        subscription_id: uuid.UUID, subscription_data: schemas.SubscriptionUpdate,
        db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    if subscription_data.student_id:
        student = db.query(models.Student).filter(models.Student.id == subscription_data.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Студент не найден",
            )

    if subscription_data.subscription_template_id:
        subscription_template = db.query(models.SubscriptionTemplate).filter(
            models.SubscriptionTemplate.id == subscription_data.subscription_template_id).first()

        if not subscription_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Шаблон подписки не найден",
            )

    for field, value in subscription_data.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)

    db.commit()
    db.refresh(subscription)

    return subscription
