from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from pydantic import AfterValidator
from sqlalchemy import exists, and_, or_, text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db, TIMEZONE
from app.models import User, Admin, SubscriptionTemplate, SubscriptionLessonType, LessonType
from app.schemas.subscriptionTemplate import *

import uuid

router = APIRouter(
    prefix='/subscriptionTemplates',
    tags=['subscription templates']
)


def check_subscription_template(subscription_template_data):
    if subscription_template_data.lesson_count and subscription_template_data.lesson_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Количество занятий в шаблоне абонемента должно быть положительным'
        )
    if subscription_template_data.expiration_day_count and subscription_template_data.expiration_day_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время действия шаблона абонемента в днях должно быть положительным'
        )
    if subscription_template_data.price and subscription_template_data.price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Стоимость шаблона абонемента должна быть неотрицательной'
        )
    if subscription_template_data.expiration_date:
        subscription_template_data.expiration_date = (
            subscription_template_data.expiration_date.astimezone(TIMEZONE)
        )


@router.post('/', response_model=SubscriptionTemplateInfo, status_code=status.HTTP_201_CREATED)
async def create_subscription_template(
        subscription_template_data: SubscriptionTemplateCreate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    check_subscription_template(subscription_template_data)

    subscription_template = SubscriptionTemplate(
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


def apply_filters_to_subscription_templates(subscription_templates, filters, db: Session):
    if filters.lesson_type_ids:
        subscription_templates = subscription_templates.where(
            exists(
                SubscriptionLessonType
            ).where(
                SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id,
                SubscriptionLessonType.lesson_type_id.in_(filters.lesson_type_ids)
            ))

    if filters.dance_style_ids:
        subscription_templates = subscription_templates.where(db.query(LessonType).join(
            SubscriptionLessonType,
            and_(
                SubscriptionLessonType.lesson_type_id == LessonType.id,
                SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id
            )
        ).where(
            LessonType.dance_style_id.in_(filters.dance_style_ids)
        ).exists())

    if filters.is_expired is not None:
        subscription_templates = subscription_templates.where(
            or_(
                SubscriptionTemplate.expiration_date == None,
                SubscriptionTemplate.expiration_date > datetime.now(TIMEZONE)
            ) != filters.is_expired)

    return subscription_templates


def check_order_by(order_by: str) -> str:
    assert order_by in ['name', 'description', 'lesson_count', 'expiration_date', 'expiration_day_count',
                        'price', 'created_at'], 'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=SubscriptionTemplatePage)
async def search_subscription_templates(
        filters: SubscriptionTemplateSearch,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_templates = db.query(SubscriptionTemplate)
    subscription_templates = apply_filters_to_subscription_templates(subscription_templates, filters, db)
    return SubscriptionTemplatePage(
        subscription_templates=subscription_templates.order_by(
            text('subscription_templates.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=subscription_templates.count()
    )


@router.post('/search/full-info', response_model=SubscriptionTemplateFullInfoPage)
async def search_subscription_templates_full_info(
        filters: SubscriptionTemplateSearch,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_templates = db.query(SubscriptionTemplate)
    subscription_templates = apply_filters_to_subscription_templates(subscription_templates, filters, db)
    return SubscriptionTemplateFullInfoPage(
        subscription_templates=subscription_templates.order_by(
            text('subscription_templates.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=subscription_templates.count()
    )


@router.get('/{subscription_template_id}', response_model=SubscriptionTemplateInfo)
async def get_subscription_template_by_id(
        subscription_template_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(SubscriptionTemplate).where(
        SubscriptionTemplate.id == subscription_template_id).first()
    if subscription_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Шаблон абонемента не найден'
        )
    return subscription_template


@router.get('/full-info/{subscription_template_id}', response_model=SubscriptionTemplateFullInfo)
async def get_subscription_template_full_info_by_id(
        subscription_template_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(SubscriptionTemplate).where(
        SubscriptionTemplate.id == subscription_template_id).first()
    if subscription_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Шаблон абонемента не найден'
        )
    return subscription_template


@router.patch('/{subscription_template_id}', response_model=SubscriptionTemplateFullInfo,
              status_code=status.HTTP_200_OK)
async def patch_subscription_template(
        subscription_template_id: uuid.UUID,
        subscription_template_data: SubscriptionTemplateUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(SubscriptionTemplate).where(
        SubscriptionTemplate.id == subscription_template_id
    ).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Шаблон абонемента не найден'
        )
    check_subscription_template(subscription_template_data)

    for field, value in subscription_template_data.model_dump(exclude_unset=True).items():
        setattr(subscription_template, field, value)

    db.commit()
    db.refresh(subscription_template)

    return subscription_template


@router.post('/lesson-types/{subscription_template_id}/{lesson_type_id}',
             response_model=SubscriptionTemplateFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_subscription_lesson_type(
        subscription_template_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(SubscriptionTemplate).where(
        SubscriptionTemplate.id == subscription_template_id
    ).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Шаблон абонемента не найден'
        )

    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип занятия не найден'
        )
    if lesson_type.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тип занятия не активен'
        )

    existing_lesson_type = db.query(SubscriptionLessonType).where(
        SubscriptionLessonType.subscription_template_id == subscription_template_id,
        SubscriptionLessonType.lesson_type_id == lesson_type_id
    ).first()
    if existing_lesson_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Шаблон абонемента уже имеет этот тип занятия'
        )

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_id,
        lesson_type_id=lesson_type_id
    )

    db.add(subscription_lesson_type)
    db.commit()
    db.refresh(subscription_template)

    return subscription_template


@router.delete('/lesson-types/{subscription_template_id}/{lesson_type_id}')
async def delete_subscription_lesson_type(
        subscription_template_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        response: Response,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    subscription_template = db.query(SubscriptionTemplate).where(
        SubscriptionTemplate.id == subscription_template_id
    ).first()
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Шаблон абонемента не найден'
        )

    lesson_type = db.query(LessonType).where(LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип занятия не найден'
        )

    existing_lesson_type = db.query(SubscriptionLessonType).where(
        SubscriptionLessonType.subscription_template_id == subscription_template.id,
        SubscriptionLessonType.lesson_type_id == lesson_type.id
    ).first()
    if not existing_lesson_type:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 'Шаблон абонемента не связан с этим типом занятия'

    db.delete(existing_lesson_type)
    db.commit()

    return 'Тип занятия успешно удалён из шаблона абонемента'
