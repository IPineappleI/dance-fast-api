import uuid
from datetime import timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import exists, or_
from sqlalchemy.orm import Session
from typing import List

from app.auth.jwt import get_current_admin, get_current_user, get_current_student
from app.database import get_db
from app import models, schemas
from app.routers.users import patch_user


router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Ученик не найден"}, 204: {"description": "Связь уже удалена"}}
)


@router.get("/", response_model=List[schemas.StudentInfo])
async def get_students(
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/full-info", response_model=List[schemas.StudentFullInfo])
async def get_students_full_info(
        skip: int = 0, limit: int = 100,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=schemas.StudentInfo)
async def get_student_by_id(
        student_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )
    return student


@router.get("/full-info/{student_id}", response_model=schemas.StudentFullInfo)
async def get_student_full_info_by_id(
        student_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )
    return student


@router.patch("/{student_id}", response_model=schemas.StudentFullInfo, status_code=status.HTTP_200_OK)
async def patch_student(
        student_id: uuid.UUID,
        student_data: schemas.StudentUpdate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )
    if student.user_id != current_user.id and not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    if student_data.level_id:
        level = db.query(models.Level).filter(models.Level.id == student_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уровень подготовки не найден",
            )
        if level.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Уровень подготовки не активен",
            )
        student.level_id = student_data.level_id
        student_data.level_id = None

    if student_data.terminated:
        db.query(models.StudentGroup).filter(models.StudentGroup.student_id == student_id).delete()

    patch_user(student.user_id, student_data, db)

    db.refresh(student)

    return student


@router.post("/groups/{student_id}/{group_id}", response_model=schemas.StudentFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_student_group(
        student_id: uuid.UUID,
        group_id: uuid.UUID,
        current_student: models.Student = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден"
        )
    if student.id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    if group.terminated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не активна"
        )
    if len(group.student_groups) >= group.max_capacity:
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

    lesson_type_ids = db.query(models.LessonType.id).join(
        models.SubscriptionLessonType
    ).join(
        models.SubscriptionTemplate
    ).join(
        models.Subscription
    ).join(
        models.Payment
    ).filter(
        models.Subscription.student_id == student.id,
        or_(
            models.Subscription.expiration_date == None,
            models.Subscription.expiration_date > datetime.now(timezone.utc)
        ),
        models.Payment.terminated == False
    ).all()
    lesson_type_ids = [lesson_type_id.id for lesson_type_id in lesson_type_ids]

    lessons_check = db.query(models.Lesson).filter(exists().where(
        models.Lesson.group_id == group.id,
        models.Lesson.start_time > datetime.now(timezone.utc),
        ~models.Lesson.lesson_type_id.in_(lesson_type_ids),
        models.Lesson.terminated == False,
        models.Lesson.is_confirmed == True
    )).first()
    if lessons_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для вступления в группу у ученика должны быть абонементы, подходящие для всех занятий группы"
        )

    student_group = models.StudentGroup(
        student_id=student_id,
        group_id=group_id
    )

    db.add(student_group)
    db.commit()
    db.refresh(student)

    return student


@router.delete("/groups/{student_id}/{group_id}")
async def delete_student_group(
        student_id: uuid.UUID,
        group_id: uuid.UUID,
        response: Response,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
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
    if group.terminated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не активна"
        )

    if student.user_id != current_user.id and not current_user.admin:
        if current_user.teacher:
            teacher_group = db.query(models.TeacherGroup).filter(
                models.TeacherGroup.teacher_id == current_user.teacher.id,
                models.TeacherGroup.group_id == group.id
            ).first()
            if not teacher_group:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Преподаватель не связан с этой группой"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )

    existing_group = db.query(models.StudentGroup).filter(
        models.StudentGroup.student_id == student_id,
        models.StudentGroup.group_id == group_id
    ).first()
    if not existing_group:
        response.status_code=status.HTTP_204_NO_CONTENT
        return "Ученик не связан с этой группой"

    db.delete(existing_group)
    db.commit()

    return "Ученик успешно удалён из группы"
