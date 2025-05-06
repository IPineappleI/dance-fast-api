from datetime import timedelta, tzinfo
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from pydantic import AfterValidator
from sqlalchemy import or_, and_, text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db, TIMEZONE
from app.routers.lessons import get_teacher_parallel_lesson
from app.models import User, Teacher, Slot, TeacherLessonType
from app.schemas.slot import *

router = APIRouter(
    prefix='/slots',
    tags=['slots']
)


def astimezone(t: time, tz: tzinfo) -> time:
    return datetime.combine(
        datetime.today(),
        t,
        t.tzinfo
    ).astimezone(tz).timetz()


def check_slot_data(slot_data, teacher_id, db: Session, existing_slot=None):
    if slot_data.start_time:
        slot_data.start_time = astimezone(slot_data.start_time, TIMEZONE)
    start_time = slot_data.start_time if slot_data.start_time else existing_slot.start_time

    if slot_data.end_time:
        slot_data.end_time = astimezone(slot_data.end_time, TIMEZONE)
    end_time = slot_data.end_time if slot_data.end_time else existing_slot.end_time

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время начала слота должно быть раньше времени конца слота'
        )

    if slot_data.day_of_week is not None and (slot_data.day_of_week < 0 or slot_data.day_of_week > 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='День недели должен принимать значения от 0 до 6'
        )

    existing_slot = db.query(Slot).where(
        Slot.id != existing_slot.id if existing_slot else True,
        Slot.teacher_id == teacher_id,
        Slot.day_of_week ==
        (slot_data.day_of_week if slot_data.day_of_week is not None else existing_slot.day_of_week),
        or_(
            and_(start_time >= Slot.start_time, start_time < Slot.end_time),
            and_(end_time > Slot.start_time, end_time <= Slot.end_time),
            and_(start_time <= Slot.start_time, end_time >= Slot.end_time)
        )
    ).first()
    if existing_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='У преподавателя есть пересекающийся с этим временем слот'
        )


@router.post('/', response_model=SlotInfo, status_code=status.HTTP_201_CREATED)
async def create_slot(
        slot_data: SlotCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).where(Teacher.id == slot_data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Преподаватель не найден'
        )
    if not current_user.admin and current_user.id != teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )

    check_slot_data(slot_data, teacher.id, db)

    slot = Slot(
        teacher_id=teacher.id,
        day_of_week=slot_data.day_of_week,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot


def apply_filters_to_slots(slots, filters, db):
    if filters.start_time:
        filters.start_time = astimezone(filters.start_time, TIMEZONE)
        slots = slots.where(Slot.start_time >= filters.start_time)
    if filters.end_time:
        filters.end_time = astimezone(filters.end_time, TIMEZONE)
        slots = slots.where(Slot.end_time <= filters.end_time)

    if filters.days_of_week:
        slots = slots.where(Slot.day_of_week.in_(filters.days_of_week))

    if filters.teacher_ids:
        slots = slots.where(Slot.teacher_id.in_(filters.teacher_ids))

    if filters.lesson_type_ids:
        slots = slots.where(
            db.query(TeacherLessonType).where(
                TeacherLessonType.teacher_id == Slot.teacher_id,
                TeacherLessonType.lesson_type_id.in_(filters.lesson_type_ids)
            ).exists()
        )

    return slots


def check_order_by(order_by: str) -> str:
    assert order_by in ['day_of_week', 'start_time', 'end_time', 'created_at'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=SlotPage)
async def search_slots(
        filters: SlotFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    slots = db.query(Slot)
    slots = apply_filters_to_slots(slots, filters, db)
    return SlotPage(
        slots=slots.order_by(
            text('slots.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=slots.count()
    )


@router.post('/search/full-info', response_model=SlotFullInfoPage)
async def search_slots_full_info(
        filters: SlotFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    slots = db.query(Slot)
    slots = apply_filters_to_slots(slots, filters, db)
    return SlotFullInfoPage(
        slots=slots.order_by(
            text('slots.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=slots.count()
    )


def get_available_slots(slots, date_from, date_to, db):
    now = datetime.now(TIMEZONE)
    date_from = date_from.astimezone(TIMEZONE)
    if date_from < now:
        date_from = now
    date_to = date_to.astimezone(TIMEZONE)

    available_slots = []
    for slot in slots:
        current_datetime = date_from
        current_datetime = current_datetime.replace(hour=slot.start_time.hour, minute=slot.start_time.minute)

        while current_datetime < now or current_datetime.weekday() != slot.day_of_week:
            current_datetime = current_datetime + timedelta(days=1)

        while current_datetime <= date_to:
            finish_datetime = current_datetime.replace(hour=slot.end_time.hour, minute=slot.end_time.minute)
            parallel_lesson = get_teacher_parallel_lesson(
                slot.teacher_id,
                current_datetime,
                finish_datetime,
                db
            )
            if not parallel_lesson:
                available_slots.append(
                    SlotAvailable(
                        teacher=slot.teacher,
                        start_time=current_datetime,
                        finish_time=finish_datetime
                    )
                )
            current_datetime = current_datetime + timedelta(days=7)

    return available_slots


@router.post('/search/available', response_model=List[SlotAvailable])
async def search_available_slots(
        filters: SlotAvailableFilters,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    filters.date_from = filters.date_from.astimezone(TIMEZONE)
    filters.date_to = filters.date_to.astimezone(TIMEZONE)
    if filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время начала поиска не может быть больше времени конца поиска'
        )
    if filters.date_to < datetime.now(TIMEZONE):
        return []

    slots = db.query(Slot)

    if filters.teacher_ids:
        slots = slots.where(Slot.teacher_id.in_(filters.teacher_ids))

    if filters.lesson_type_ids:
        slots = slots.where(
            db.query(TeacherLessonType).where(
                TeacherLessonType.teacher_id == Slot.teacher_id,
                TeacherLessonType.lesson_type_id.in_(filters.lesson_type_ids)
            ).exists()
        )

    return get_available_slots(slots.all(), filters.date_from, filters.date_to, db)


@router.get('/{slot_id}', response_model=SlotInfo)
async def get_slot_by_id(
        slot_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    slot = db.query(Slot).where(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Слот не найден'
        )
    return slot


@router.get('/full-info/{slot_id}', response_model=SlotFullInfo)
async def get_slot_full_info_by_id(
        slot_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    slot = db.query(Slot).where(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Слот не найден'
        )
    return slot


@router.delete('/{slot_id}')
async def delete_slot_by_id(
        slot_id: uuid.UUID,
        response: Response,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    slot = db.query(Slot).where(Slot.id == slot_id).first()
    if not slot:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 'Слот уже удалён'

    if not current_user.admin and current_user.id != slot.teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )

    db.delete(slot)
    db.commit()

    return 'Слот успешно удалён'


@router.patch('/{slot_id}', response_model=SlotFullInfo)
async def patch_slot(
        slot_id: uuid.UUID,
        slot_data: SlotUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    slot = db.query(Slot).where(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Слот не найден'
        )
    teacher = slot.teacher
    if slot_data.teacher_id:
        teacher = db.query(Teacher).where(Teacher.id == slot_data.teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Преподаватель не найден'
            )
    if not current_user.admin and current_user.id != teacher.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав'
        )

    check_slot_data(slot_data, teacher.id, db, slot)

    for field, value in slot_data.model_dump(exclude_unset=True).items():
        setattr(slot, field, value)

    db.commit()
    db.refresh(slot)

    return slot
