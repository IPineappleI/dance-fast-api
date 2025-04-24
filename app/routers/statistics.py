from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.auth.jwt import get_current_admin
from app.database import get_db

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)


@router.post("/subscriptions", response_model=List[schemas.SubscriptionPurchasesInterval])
async def get_subscription_purchases_statistics(
        filters: schemas.SubscriptionPurchasesFilters,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата начала составления выборки не может быть позже даты конца"
        )

    if filters.interval_in_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Интервал статистической выборки в днях должен быть положительным"
        )

    statistics: List[schemas.SubscriptionPurchasesInterval] = []

    interval_date_from = filters.date_from
    while interval_date_from <= filters.date_to:
        interval_date_to = interval_date_from + timedelta(days=filters.interval_in_days)
        interval_statistics = db.query(
            func.count(models.Payment.id).label('count'),
            func.sum(models.SubscriptionTemplate.price).label('sum')
        ).join(
            models.Subscription,
            models.Subscription.payment_id == models.Payment.id
        ).join(
            models.SubscriptionTemplate,
            models.SubscriptionTemplate.id == models.Subscription.subscription_template_id
        ).filter(and_(
            models.Payment.created_at >= interval_date_from,
            models.Payment.created_at < interval_date_to,
            models.Payment.created_at < filters.date_to + timedelta(days=1)
        ))

        if filters.is_group is not None or filters.dance_style_ids:
            interval_statistics = interval_statistics.filter(db.query(models.LessonType).join(
                models.SubscriptionLessonType,
                and_(models.SubscriptionLessonType.lesson_type_id == models.LessonType.id,
                     models.SubscriptionLessonType.subscription_template_id == models.SubscriptionTemplate.id)
            ).where(and_(
                (models.LessonType.is_group == filters.is_group) if filters.is_group is not None else True,
                (models.LessonType.dance_style_id.in_(filters.dance_style_ids)) if filters.dance_style_ids else True
            )).exists())

        if filters.subscription_template_ids:
            interval_statistics = interval_statistics.filter(
                models.SubscriptionTemplate.id.in_(filters.subscription_template_ids)
            )

        interval_statistics = interval_statistics.first()
        interval_statistics = schemas.SubscriptionPurchasesInterval(
            date_from=interval_date_from,
            date_to=(
                interval_date_to - timedelta(days=1) if interval_date_to - timedelta(days=1) <= filters.date_to
                else filters.date_to
            ),
            count=interval_statistics.count if interval_statistics and interval_statistics.count else 0,
            sum=interval_statistics.sum if interval_statistics and interval_statistics.sum else 0
        )

        statistics.append(interval_statistics)

        interval_date_from = interval_date_to

    return statistics
