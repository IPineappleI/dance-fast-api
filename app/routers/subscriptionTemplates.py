from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

import uuid


router = APIRouter(
    prefix="/subscriptionTemplates",
    tags=["subscription templates"],
    responses={404: {"description": "Шаблон абонемента не найден"}}
)


@router.post("/", response_model=schemas.SubscriptionTemplateFullInfo, status_code=status.HTTP_201_CREATED)
async def create_subscription_template(
        subscription_template_data: schemas.SubscriptionTemplateBase,
        db: Session = Depends(get_db)
):
    subscription_template = models.SubscriptionTemplate(
        name=subscription_template_data.name,
        description=subscription_template_data.description,
        lesson_count=subscription_template_data.lesson_count,
        expiration_date=subscription_template_data.expiration_date,
        expiration_day_count=subscription_template_data.expiration_day_count,
        price=subscription_template_data.price
    )

    db.add(subscription_template)
    db.commit()
    db.refresh(subscription_template)

    return subscription_template


@router.get("/", response_model=List[schemas.SubscriptionTemplateFullInfo])
async def get_all_subscription_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscription_templates = db.query(models.SubscriptionTemplate).offset(skip).limit(limit).all()
    return subscription_templates


@router.get("/{subscription_template_id}", response_model=schemas.SubscriptionTemplateFullInfo)
async def get_subscription_template_by_id(subscription_template_id: uuid.UUID, db: Session = Depends(get_db)):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id).first()
    if subscription_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон абонемента не найден"
        )
    return subscription_template


@router.patch("/{subscription_template_id}", response_model=schemas.SubscriptionTemplateFullInfo,
              status_code=status.HTTP_200_OK)
async def patch_subscription_template(subscription_template_id: uuid.UUID,
                                      subscription_template_data: schemas.SubscriptionTemplateUpdate,
                                      db: Session = Depends(get_db)):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон абонемента не найден"
        )

    for field, value in subscription_template_data.model_dump(exclude_unset=True).items():
        setattr(subscription_template, field, value)

    db.commit()
    db.refresh(subscription_template)

    return subscription_template


@router.post("/lesson-types/{subscription_template_id}/{lesson_type_id}",
             response_model=schemas.SubscriptionTemplateFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_subscription_lesson_type(
        subscription_template_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id).first()

    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон абонемента не найден"
        )

    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тип занятия не найден"
        )

    existing_lesson_type = db.query(models.SubscriptionLessonType).filter(
        models.SubscriptionLessonType.subscription_template_id == subscription_template_id,
        models.SubscriptionLessonType.lesson_type_id == lesson_type_id
    ).first()

    if existing_lesson_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Шаблон абонемента уже имеет этот тип занятия"
        )

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_id,
        lesson_type_id=lesson_type_id
    )

    db.add(subscription_lesson_type)
    db.commit()
    db.refresh(subscription_template)

    return subscription_template
