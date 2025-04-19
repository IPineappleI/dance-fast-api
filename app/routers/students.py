import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.routers.users import patch_user

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Ученик не найден"}}
)


@router.post("/", response_model=schemas.StudentInfo, status_code=status.HTTP_201_CREATED)
async def create_student(
        student_data: schemas.StudentBase,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == student_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователя с идентификатором {student_data.user_id} не существует",
        )

    level = db.query(models.Level).filter(models.Level.id == student_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Уровня подготовки с идентификатором {student_data.level_id} не существует",
        )

    student = models.Student(
        user_id=student_data.user_id,
        level_id=student_data.level_id
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


@router.get("/", response_model=List[schemas.StudentInfo])
async def get_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/full-info", response_model=List[schemas.StudentFullInfo])
async def get_all_students_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=schemas.StudentInfo)
async def get_student_by_id(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )
    return student


@router.get("/full-info/{student_id}", response_model=schemas.StudentFullInfo)
async def get_student_full_info_by_id(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )

    return student


@router.patch("/{student_id}", response_model=schemas.StudentInfo, status_code=status.HTTP_200_OK)
async def patch_student(student_id: uuid.UUID, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )

    if student_data.level_id:
        level = db.query(models.Level).filter(models.Level.id == student_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уровень не найден",
            )
        setattr(student, "level_id", student_data.level_id)
        student_data.level_id = None

    await patch_user(student.user_id, student_data, db)

    db.commit()
    db.refresh(student)

    return student


@router.post("/groups/{student_id}/{group_id}", response_model=schemas.StudentFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_student_group(
        student_id: uuid.UUID,
        group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    student = db.query(models.Student).options().filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    if len(group.students) >= group.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В группе нет свободных мест"
        )

    existing_group = db.query(models.StudentGroup).filter(
        models.StudentGroup.student_id == student_id,
        models.StudentGroup.group_id == group_id
    ).first()

    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ученик уже связан с этой группой"
        )

    student_group = models.StudentGroup(
        student_id=student_id,
        group_id=group_id
    )

    db.add(student_group)
    db.commit()
    db.refresh(student)

    return student
