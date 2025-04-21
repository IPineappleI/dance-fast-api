from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db

import uuid

from app.schemas import SlotAvailable

router = APIRouter(
    prefix="/slots",
    tags=["slots"],
    responses={404: {"description": "Слот не найден"}, 204: {"description": "Слот уже удалён"}}
)


@router.post("/", response_model=schemas.SlotInfo, status_code=status.HTTP_201_CREATED)
async def create_slot(
        slot_data: schemas.SlotBase,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == slot_data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    if slot_data.day_of_week < 0 or slot_data.day_of_week > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="День недели должен принимать значения от 0 до 6"
        )

    if slot_data.start_time.tzinfo != slot_data.end_time.tzinfo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала слота должно быть в том же часовом поясе, что и время конца слота"
        )

    if slot_data.start_time >= slot_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала слота должно быть раньше времени конца слота"
        )

    slot = models.Slot(
        teacher_id=slot_data.teacher_id,
        day_of_week=slot_data.day_of_week,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot


@router.post("/search/available", response_model=List[schemas.SlotAvailable])
async def search_available_slots(
        filters: schemas.SlotSearch,
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    if filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала поиска не может быть больше времени конца поиска"
        )

    slots = db.query(models.Slot)

    if filters.teacher_ids:
        slots = slots.filter(models.Slot.teacher_id.in_(filters.teacher_ids))

    if filters.lesson_type_ids:
        slots = slots.join(
            models.Teacher,
            models.Slot.teacher_id == models.Teacher.id
        ).join(
            models.TeacherLessonType,
            models.Teacher.id == models.TeacherLessonType.teacher_id
        ).filter(
            models.TeacherLessonType.lesson_type_id.in_(filters.lesson_type_ids)
        )

    slots = slots.offset(skip).limit(limit).all()

    available_slots = []
    for slot in slots:
        tz = slot.start_time.tzinfo
        date_from = filters.date_from.astimezone(tz)
        date_to = filters.date_to.astimezone(tz)
        now = datetime.now(tz)

        current_datetime = date_from
        current_datetime = current_datetime.replace(hour=slot.start_time.hour, minute=slot.start_time.minute)

        while current_datetime.weekday() != slot.day_of_week:
            current_datetime = current_datetime + timedelta(days=1)

        while current_datetime <= date_to:
            if current_datetime >= date_from and current_datetime >= now:
                finish_datetime = current_datetime.replace(hour=slot.end_time.hour, minute=slot.end_time.minute)
                if finish_datetime <= date_to:
                    available_slots.append(
                        SlotAvailable(
                            teacher=slot.teacher,
                            start_time=current_datetime,
                            finish_time=finish_datetime
                        )
                    )

            current_datetime = current_datetime + timedelta(days=7)

    return available_slots


@router.get("/", response_model=List[schemas.SlotInfo])
async def get_slots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    slots = db.query(models.Slot).offset(skip).limit(limit).all()
    return slots


@router.get("/full-info", response_model=List[schemas.SlotFullInfo])
async def get_slots_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    slots = db.query(models.Slot).offset(skip).limit(limit).all()
    return slots


@router.get("/{slot_id}", response_model=schemas.SlotInfo)
async def get_slot_by_id(slot_id: uuid.UUID, db: Session = Depends(get_db)):
    slot = db.query(models.Slot).filter(models.Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден"
        )
    return slot


@router.get("/full-info/{slot_id}", response_model=schemas.SlotFullInfo)
async def get_slot_full_info_by_id(slot_id: uuid.UUID, db: Session = Depends(get_db)):
    slot = db.query(models.Slot).filter(models.Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден"
        )
    return slot


@router.get("/by-teacher/{teacher_id}", response_model=List[schemas.SlotInfo])
async def get_slots_by_teacher_id(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    slots = db.query(models.Slot).filter(models.Slot.teacher_id == teacher_id).all()

    return slots


@router.delete("/{slot_id}")
async def delete_slot_by_id(slot_id: uuid.UUID, response: Response, db: Session = Depends(get_db)):
    slot = db.query(models.Slot).filter(models.Slot.id == slot_id).first()
    if not slot:
        response.status_code = status.HTTP_204_NO_CONTENT
        return "Слот уже удалён"

    db.delete(slot)
    db.commit()

    return "Слот успешно удалён"


@router.patch("/{slot_id}", response_model=schemas.SlotInfo, status_code=status.HTTP_200_OK)
async def patch_slot(
        slot_id: uuid.UUID,
        slot_data: schemas.SlotUpdate,
        db: Session = Depends(get_db)
):
    slot = db.query(models.Slot).filter(models.Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден"
        )

    if slot_data.teacher_id:
        teacher = db.query(models.Teacher).filter(models.Teacher.id == slot_data.teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Преподаватель не найден"
            )

    if slot_data.day_of_week:
        if slot_data.day_of_week < 0 or slot_data.day_of_week > 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="День недели должен принимать значения от 0 до 6"
            )

    for field, value in slot_data.model_dump(exclude_unset=True).items():
        setattr(slot, field, value)

    if slot.start_time >= slot.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Левая граница слота должна быть раньше правой"
        )

    db.commit()
    db.refresh(slot)

    return slot
