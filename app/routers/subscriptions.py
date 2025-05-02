from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import AfterValidator
from sqlalchemy import or_, text
from sqlalchemy.orm import Session
from datetime import timedelta

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db, TIMEZONE
from app.routers.lessons import get_student_parallel_lesson
from app.models import User, Admin, Student, Subscription, SubscriptionTemplate, Payment, Lesson
from app.models.association import *
from app.schemas.subscription import *
from app.schemas import LessonFullInfo

import uuid

router = APIRouter(
    prefix='/subscriptions',
    tags=['subscriptions']
)


def check_subscription_template(subscription_template):
    if not subscription_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Шаблон абонемента не найден'
        )
    if (subscription_template.expiration_date and
            subscription_template.expiration_date <= datetime.now(TIMEZONE)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Шаблон абонемента не активен'
        )


def check_payment(payment):
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Платёж не найден'
        )
    if payment.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Платёж отменён'
        )


def check_subscription(subscription, current_user):
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Абонемент не найден'
        )
    if not current_user.admin and current_user.id != subscription.student.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )
    if subscription.expiration_date and subscription.expiration_date <= datetime.now(TIMEZONE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Абонемент не активен'
        )


@router.post('/', response_model=SubscriptionInfo, status_code=status.HTTP_201_CREATED)
async def create_subscription(
        subscription_data: SubscriptionCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == subscription_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ученик не найден'
        )
    if not current_user.admin and current_user.id != student.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )

    subscription_template = db.query(SubscriptionTemplate).where(
        SubscriptionTemplate.id == subscription_data.subscription_template_id
    ).first()
    check_subscription_template(subscription_template)

    payment = db.query(Payment).where(Payment.id == subscription_data.payment_id).first()
    check_payment(payment)

    subscription = Subscription(
        student_id=student.id,
        subscription_template_id=subscription_template.id,
        payment_id=payment.id
    )

    if subscription_template.expiration_day_count:
        subscription.expiration_date = (datetime.now(TIMEZONE) +
                                        timedelta(days=subscription_template.expiration_day_count))

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def apply_filters_to_subscriptions(subscriptions, filters):
    if filters.student_id:
        subscriptions = subscriptions.where(Subscription.student_id == filters.student_id)

    if filters.subscription_template_ids:
        subscriptions = subscriptions.where(
            Subscription.subscription_template_id.in_(filters.subscription_template_ids)
        )

    if filters.is_paid is not None:
        subscriptions = subscriptions.where((Subscription.payment_id != None) == filters.is_paid)

    if filters.is_expired is not None:
        subscriptions = subscriptions.where(
            or_(
                Subscription.expiration_date == None,
                Subscription.expiration_date > datetime.now(TIMEZONE)
            ) != filters.is_expired
        )

    return subscriptions


def check_order_by(order_by: str) -> str:
    assert order_by in ['expiration_date', 'created_at'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=SubscriptionPage)
async def search_subscriptions(
        filters: SubscriptionFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscriptions = db.query(Subscription)
    subscriptions = apply_filters_to_subscriptions(subscriptions, filters)
    return SubscriptionPage(
        subscriptions=subscriptions.order_by(
            text('subscriptions.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=subscriptions.count()
    )


@router.post('/search/full-info', response_model=SubscriptionFullInfoPage)
async def search_subscriptions_full_info(
        filters: SubscriptionFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscriptions = db.query(Subscription)
    subscriptions = apply_filters_to_subscriptions(subscriptions, filters)
    return SubscriptionFullInfoPage(
        subscriptions=subscriptions.order_by(
            text('subscriptions.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=subscriptions.count()
    )


@router.get('/{subscription_id}', response_model=SubscriptionInfo)
async def get_subscription_by_id(
        subscription_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).where(Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Абонемент не найден'
        )
    return subscription


@router.get('/full-info/{subscription_id}', response_model=SubscriptionFullInfo)
async def get_subscription_full_info_by_id(
        subscription_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).where(Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Абонемент не найден'
        )
    return subscription


@router.patch('/{subscription_id}', response_model=SubscriptionFullInfo)
async def patch_subscription(
        subscription_id: uuid.UUID,
        subscription_data: SubscriptionUpdate,
        current_admin: Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).where(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Абонемент не найден'
        )

    if subscription_data.subscription_template_id:
        subscription_template = db.query(SubscriptionTemplate).where(
            SubscriptionTemplate.id == subscription_data.subscription_template_id
        ).first()
        check_subscription_template(subscription_template)

    if subscription_data.payment_id:
        payment = db.query(Payment).where(Payment.id == subscription_data.payment_id).first()
        check_payment(payment)

    for field, value in subscription_data.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)

    db.commit()
    db.refresh(subscription)

    return subscription


@router.post('/lessons/{subscription_id}/{lesson_id}', response_model=LessonFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_lesson_subscription(
        subscription_id: uuid.UUID,
        lesson_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).where(Subscription.id == subscription_id).first()
    check_subscription(subscription, current_user)
    if subscription.lessons_left <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В абонементе не осталось занятий'
        )

    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )
    if lesson.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Занятие отменено'
        )

    if lesson.lesson_type not in subscription.subscription_template.lesson_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Данный абонемент не подходит для этого занятия'
        )

    if lesson.group_id and subscription.student not in lesson.group.students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ученик не является членом группы'
        )

    existing_lesson_subscription = db.query(LessonSubscription).join(Subscription).where(
        Subscription.student_id == subscription.student_id,
        LessonSubscription.lesson_id == lesson.id,
        LessonSubscription.cancelled == False
    ).first()
    if existing_lesson_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ученик уже записан на это занятие'
        )

    parallel_student_lesson = get_student_parallel_lesson(
        subscription.student_id, lesson.start_time, lesson.finish_time, db
    )
    if parallel_student_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ученик уже записан на пересекающееся по времени занятие'
        )

    lesson_subscription = LessonSubscription(
        subscription_id=subscription_id,
        lesson_id=lesson_id
    )
    db.add(lesson_subscription)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.patch('/lessons/cancel/{subscription_id}/{lesson_id}',
              response_model=SubscriptionFullInfo,
              status_code=status.HTTP_200_OK)
async def cancel_lesson_subscription(
        subscription_id: uuid.UUID,
        lesson_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).where(Subscription.id == subscription_id).first()
    check_subscription(subscription, current_user)

    lesson = db.query(Lesson).where(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Занятие не найдено'
        )
    if lesson.start_time <= datetime.now(TIMEZONE) and not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Занятие уже началось'
        )

    lesson_subscription = db.query(LessonSubscription).where(
        LessonSubscription.subscription_id == subscription.id,
        LessonSubscription.lesson_id == lesson.id
    ).first()
    if not lesson_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Абонемент не связан с данным занятием'
        )

    if not lesson.group_id:
        db.query(TeacherLesson).where(
            TeacherLesson.lesson_id == lesson_id
        ).delete()

        lesson.terminated = True

    lesson_subscription.cancelled = True

    db.commit()
    db.refresh(subscription)

    return subscription
