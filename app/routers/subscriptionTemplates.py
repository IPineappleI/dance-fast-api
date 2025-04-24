from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import exists, and_
from sqlalchemy.orm import Session, Query
from typing import List

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app import models, schemas

import uuid


router = APIRouter(
    prefix="/subscriptionTemplates",
    tags=["subscription templates"],
    responses={404: {"description": "Шаблон абонемента не найден"}}
)


def check_subscription_template(subscription_template_data):
    if subscription_template_data.lesson_count and subscription_template_data.lesson_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество занятий в шаблоне абонемента должно быть положительным"
        )
    if subscription_template_data.expiration_day_count and subscription_template_data.expiration_day_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время действия шаблона абонемента в днях должно быть положительным"
        )
    if subscription_template_data.price and subscription_template_data.price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Стоимость шаблона абонемента должна быть неотрицательной"
        )

@router.post("/", response_model=schemas.SubscriptionTemplateInfo, status_code=status.HTTP_201_CREATED)
async def create_subscription_template(
        subscription_template_data: schemas.SubscriptionTemplateBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    check_subscription_template(subscription_template_data)

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


def apply_filters_to_subscription_templates(subscription_templates: Query, filters, db: Session):
    if filters.lesson_type_ids:
        subscription_templates = subscription_templates.filter(
            exists(
                models.SubscriptionLessonType
            ).where(
                models.SubscriptionLessonType.subscription_template_id == models.SubscriptionTemplate.id,
                models.SubscriptionLessonType.lesson_type_id.in_(filters.lesson_type_ids)
        ))

    if filters.dance_style_ids:
        subscription_templates = subscription_templates.filter(db.query(models.LessonType).join(
            models.SubscriptionLessonType,
            and_(
                models.SubscriptionLessonType.lesson_type_id == models.LessonType.id,
                models.SubscriptionLessonType.subscription_template_id == models.SubscriptionTemplate.id
            )
        ).where(
            models.LessonType.dance_style_id.in_(filters.dance_style_ids)
        ).exists())

    return subscription_templates


@router.post("/search", response_model=List[schemas.SubscriptionTemplateInfo])
async def search_subscription_templates(
        filters: schemas.SubscriptionTemplateSearch,
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_templates = db.query(models.SubscriptionTemplate)
    subscription_templates = apply_filters_to_subscription_templates(subscription_templates, filters, db)
    subscription_templates = subscription_templates.offset(skip).limit(limit).all()
    return subscription_templates


@router.post("/search/full-info", response_model=List[schemas.SubscriptionTemplateFullInfo])
async def search_subscription_templates_full_info(
        filters: schemas.SubscriptionTemplateSearch,
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_templates = db.query(models.SubscriptionTemplate)
    subscription_templates = apply_filters_to_subscription_templates(subscription_templates, filters, db)
    subscription_templates = subscription_templates.offset(skip).limit(limit).all()
    return subscription_templates


@router.get("/{subscription_template_id}", response_model=schemas.SubscriptionTemplateInfo)
async def get_subscription_template_by_id(
        subscription_template_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id).first()
    if subscription_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон абонемента не найден"
        )
    return subscription_template


@router.get("/full-info/{subscription_template_id}", response_model=schemas.SubscriptionTemplateFullInfo)
async def get_subscription_template_full_info_by_id(
        subscription_template_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
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
async def patch_subscription_template(
        subscription_template_id: uuid.UUID,
        subscription_template_data: schemas.SubscriptionTemplateUpdate,
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id
    ).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон абонемента не найден"
        )
    check_subscription_template(subscription_template_data)

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
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id
    ).first()
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
    if lesson_type.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тип занятия не активен"
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


@router.delete("/lesson-types/{subscription_template_id}/{lesson_type_id}")
async def delete_subscription_lesson_type(
        subscription_template_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        response: Response,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(models.SubscriptionTemplate).filter(
        models.SubscriptionTemplate.id == subscription_template_id
    ).first()
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
    if lesson_type.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тип занятия не активен"
        )

    existing_lesson_type = db.query(models.SubscriptionLessonType).filter(
        models.SubscriptionLessonType.subscription_template_id == subscription_template.id,
        models.SubscriptionLessonType.lesson_type_id == lesson_type.id
    ).first()
    if not existing_lesson_type:
        response.status_code=status.HTTP_204_NO_CONTENT
        return "Шаблон абонемента не связан с этим типом занятия"

    db.delete(existing_lesson_type)
    db.commit()

    return "Тип занятия из шаблона абонемента удалён успешно"
