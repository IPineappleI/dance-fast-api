from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta

from app.auth.jwt import get_current_student
from app.database import get_db
from app import models, schemas

import uuid


router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    responses={404: {"description": "Абонемент не найден"}}
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон абонемента не найден"
        )

    if subscription_template.expiration_date and subscription_template.expiration_date <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Шаблон абонемента не активен"
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
            detail="Платёж не найден"
        )

    subscription = models.Subscription(
        student_id=student.id,
        subscription_template_id=subscription_template.id,
        payment_id=payment.id
    )

    if subscription_template.expiration_day_count:
        subscription.expiration_date = datetime.now(timezone.utc) + timedelta(days=subscription_template.expiration_day_count)

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.get("/", response_model=List[schemas.SubscriptionInfo])
async def get_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).offset(skip).limit(limit).all()
    return subscriptions


@router.get("/full-info", response_model=List[schemas.SubscriptionFullInfo])
async def get_subscriptions_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).offset(skip).limit(limit).all()
    return subscriptions


@router.get("/student/full-info/{student_id}", response_model=List[schemas.SubscriptionFullInfo])
async def get_subscriptions_full_info_by_student_id(
        student_id: uuid.UUID,
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    subscriptions = db.query(models.Subscription).filter(and_(
        models.Subscription.student_id == student_id,
        or_(models.Subscription.expiration_date == None, models.Subscription.expiration_date > now),
        models.Subscription.lessons_left > 0
    )).offset(skip).limit(limit).all()
    return subscriptions


@router.get("/{subscription_id}", response_model=schemas.SubscriptionInfo)
async def get_subscription_by_id(subscription_id: uuid.UUID, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не найден"
        )
    return subscription


@router.get("/full-info/{subscription_id}", response_model=schemas.SubscriptionFullInfo)
async def get_subscription_full_info_by_id(subscription_id: uuid.UUID, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не найден"
        )
    return subscription


@router.patch("/{subscription_id}", response_model=schemas.SubscriptionFullInfo, status_code=status.HTTP_200_OK)
async def patch_subscription(
        subscription_id: uuid.UUID,
        subscription_data: schemas.SubscriptionUpdate,
        db: Session = Depends(get_db)
):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не найден"
        )

    if subscription_data.subscription_template_id:
        subscription_template = db.query(models.SubscriptionTemplate).filter(
            models.SubscriptionTemplate.id == subscription_data.subscription_template_id).first()
        if not subscription_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон абонемента не найден"
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
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не найден"
        )
    if subscription.lessons_left <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В абонементе не осталось занятий"
        )

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    if lesson.lesson_type not in subscription.subscription_template.lesson_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Данный абонемент не подходит для этого занятия"
        )

    if lesson.group_id and subscription.student not in lesson.group.students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ученик не является членом группы"
        )

    existing_lesson_subscription = db.query(models.LessonSubscription).join(
        models.Subscription, and_(
            models.Subscription.id == models.LessonSubscription.subscription_id,
            models.Subscription.student_id == subscription.student_id
        )
    ).filter(and_(
        models.LessonSubscription.cancelled == False,
        models.LessonSubscription.lesson_id == lesson.id
    )).first()

    if existing_lesson_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ученик уже записан на это занятие"
        )

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription_id,
        lesson_id=lesson_id
    )
    db.add(lesson_subscription)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.patch("/lessons/cancel/{subscription_id}/{lesson_id}",
              response_model=schemas.SubscriptionFullInfo,
              status_code=status.HTTP_200_OK)
async def cancel_subscription_use(
        subscription_id: uuid.UUID,
        lesson_id: uuid.UUID,
        current_student: models.Student = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не найден"
        )
    if subscription.student_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Абонемент оформлен другим учеником"
        )

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    lesson_subscription = db.query(models.LessonSubscription).filter(and_(
        models.LessonSubscription.subscription_id == subscription.id,
        models.LessonSubscription.lesson_id == lesson.id,
    )).first()
    if not lesson_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Абонемент не связан с данным занятием"
        )

    lesson_subscription.cancelled = True

    db.commit()
    db.refresh(subscription)

    return subscription
