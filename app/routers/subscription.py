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


@router.post("/", response_model=schemas.SubscriptionFullInfo, status_code=status.HTTP_201_CREATED)
async def create_subscription(
        subscription_data: schemas.SubscriptionBase,
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_data.subscription_template_id).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Шаблон подписки с идентификатором {subscription_data.subscription_template_id} не найден",
        )
    if not subscription_template.active:
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден"
        )
    payment = db.query(models.Payment).filter(models.Payment.id == subscription_data.payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
        payment_id=payment.id
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
    return subscriptions


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

    return subscription


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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден",
            )

    if subscription_data.subscription_template_id:
        subscription_template = db.query(models.SubscriptionTemplate).filter(
            models.SubscriptionTemplate.id == subscription_data.subscription_template_id).first()

        if not subscription_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон подписки не найден",
            )

    for field, value in subscription_data.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)

    db.commit()
    db.refresh(subscription)

    return subscription


@router.post("/lessons/{subscription_id}/{lesson_id}", response_model=schemas.LessonFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_lesson_subscription(
        subscription_id: uuid.UUID,
        lesson_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    subscription = db.query(models.Subscription).options().filter(models.Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не найден"
        )

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    existing_lesson = db.query(models.LessonSubscription).filter(
        models.LessonSubscription.subscription_id == subscription_id,
        models.LessonSubscription.lesson_id == lesson_id
    ).first()

    if existing_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Абонемент уже связан с этим занятием"
        )

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription_id,
        lesson_id=lesson_id
    )

    db.add(lesson_subscription)
    db.commit()
    db.refresh(lesson)

    return lesson
