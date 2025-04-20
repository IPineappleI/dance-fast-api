from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db

import uuid


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

    if slot_data.start_time >= slot_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Левая граница слота должна быть раньше правой"
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


@router.get("/", response_model=List[schemas.SlotInfo])
async def get_all_slots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    slots = db.query(models.Slot).offset(skip).limit(limit).all()
    return slots


@router.get("/byTeacher/{teacher_id}", response_model=List[schemas.SlotInfo])
async def get_all_slots_by_teacher_id(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    slots = db.query(models.Slot).filter(models.Slot.teacher_id == teacher_id).all()

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
async def patch_slot(slot_id: uuid.UUID, slot_data: schemas.SlotUpdate, db: Session = Depends(get_db)):
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
