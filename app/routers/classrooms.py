from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, and_, or_
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db

import uuid


router = APIRouter(
    prefix="/classrooms",
    tags=["classrooms"],
    responses={404: {"description": "Зал не найден"}}
)


@router.post("/", response_model=schemas.ClassroomInfo, status_code=status.HTTP_201_CREATED)
async def create_classroom(
        classroom_data: schemas.ClassroomBase,
        db: Session = Depends(get_db)
):
    classroom = models.Classroom(
        name=classroom_data.name,
        description=classroom_data.description
    )

    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return classroom


@router.post("/search/available", response_model=List[schemas.ClassroomInfo])
async def search_available_classrooms(filters: schemas.ClassroomSearch,
                                      skip: int = 0, limit: int = 100,
                                      db: Session = Depends(get_db)):
    if filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала поиска не может быть больше времени конца поиска"
        )

    classrooms = db.query(models.Classroom).filter(~exists(models.Lesson).where(and_(
        models.Lesson.classroom_id == models.Classroom.id,
        models.Lesson.are_neighbours_allowed == False,
        or_(
            and_(filters.date_from >= models.Lesson.start_time, filters.date_from < models.Lesson.finish_time),
            and_(filters.date_to > models.Lesson.start_time, filters.date_to <= models.Lesson.finish_time),
            and_(filters.date_from <= models.Lesson.start_time, filters.date_to >= models.Lesson.finish_time)
        )
    ))).offset(skip).limit(limit).all()

    return classrooms


@router.get("/{classroom_id}", response_model=schemas.ClassroomInfo)
async def get_classroom_by_id(classroom_id: uuid.UUID, db: Session = Depends(get_db)):
    classroom = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зал не найден"
        )
    return classroom


@router.patch("/{classroom_id}", response_model=schemas.ClassroomInfo, status_code=status.HTTP_200_OK)
async def patch_classroom(classroom_id: uuid.UUID,
                          classroom_data: schemas.ClassroomUpdate,
                          db: Session = Depends(get_db)):
    classroom = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зал не найден"
        )

    for field, value in classroom_data.model_dump(exclude_unset=True).items():
        setattr(classroom, field, value)

    db.commit()
    db.refresh(classroom)
    return classroom
