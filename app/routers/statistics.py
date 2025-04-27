from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_admin
from app.database import get_db
from app.models import *
from app.schemas.statistics import *

router = APIRouter(
    prefix='/statistics',
    tags=['statistics']
)


@router.post('/subscriptions', response_model=List[SubscriptionPurchasesInterval])
async def get_subscription_purchases_statistics(
        filters: SubscriptionPurchasesFilters,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Дата начала составления выборки не может быть позже даты конца'
        )
    if filters.interval_in_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Интервал статистической выборки в днях должен быть положительным'
        )

    statistics: List[SubscriptionPurchasesInterval] = []

    interval_date_from = filters.date_from
    while interval_date_from <= filters.date_to:
        interval_date_to = interval_date_from + timedelta(days=filters.interval_in_days)
        interval_statistics = db.query(
            func.count(Payment.id).label('count'),
            func.sum(SubscriptionTemplate.price).label('sum')
        ).join(
            Subscription,
            Subscription.payment_id == Payment.id
        ).join(
            SubscriptionTemplate,
            SubscriptionTemplate.id == Subscription.subscription_template_id
        ).where(
            Payment.created_at >= interval_date_from,
            Payment.created_at < interval_date_to,
            Payment.created_at < filters.date_to + timedelta(days=1)
        )

        if filters.is_group is not None or filters.dance_style_ids:
            interval_statistics = interval_statistics.where(db.query(LessonType).join(
                SubscriptionLessonType,
                and_(SubscriptionLessonType.lesson_type_id == LessonType.id,
                     SubscriptionLessonType.subscription_template_id == SubscriptionTemplate.id)
            ).where(
                (LessonType.is_group == filters.is_group) if filters.is_group is not None else True,
                (LessonType.dance_style_id.in_(filters.dance_style_ids)) if filters.dance_style_ids else True
            ).exists())

        if filters.subscription_template_ids:
            interval_statistics = interval_statistics.where(
                SubscriptionTemplate.id.in_(filters.subscription_template_ids)
            )

        interval_statistics = interval_statistics.first()
        interval_statistics = SubscriptionPurchasesInterval(
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
