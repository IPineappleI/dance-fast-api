import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.routers.users import patch_user


router = APIRouter(
    prefix="/teachers",
    tags=["teachers"],
    responses={404: {"description": "Преподаватель не найден"}, 204: {"description": "Связь уже удалена"}}
)


@router.post("/", response_model=schemas.TeacherInfo, status_code=status.HTTP_201_CREATED)
async def create_teacher(
        teacher_data: schemas.TeacherBase,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == teacher_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    teacher = models.Teacher(
        user_id=teacher_data.user_id
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher


@router.get("/", response_model=List[schemas.TeacherInfo])
async def get_all_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/full-info", response_model=List[schemas.TeacherFullInfo])
async def get_all_teachers_full_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/{teacher_id}", response_model=schemas.TeacherInfo)
async def get_teacher_by_id(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )
    return teacher


@router.get("/full-info/{teacher_id}", response_model=schemas.TeacherFullInfo)
async def get_teacher_full_info_by_id(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    return teacher


@router.patch("/{teacher_id}", response_model=schemas.TeacherInfo, status_code=status.HTTP_200_OK)
async def patch_teacher(teacher_id: uuid.UUID, teacher_data: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    await patch_user(teacher.user_id, teacher_data, db)

    db.commit()
    db.refresh(teacher)

    return teacher


@router.post("/lesson-types/{teacher_id}/{lesson_type_id}", response_model=schemas.TeacherFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_teacher_lesson_type(
        teacher_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).options().filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стиль танца не найден"
        )

    existing_lesson_type = db.query(models.TeacherLessonType).filter(
        models.TeacherLessonType.teacher_id == teacher_id,
        models.TeacherLessonType.lesson_type_id == lesson_type_id
    ).first()

    if existing_lesson_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель уже имеет этот стиль танца"
        )

    teacher_lesson_type = models.TeacherLessonType(
        teacher_id=teacher_id,
        lesson_type_id=lesson_type_id
    )

    db.add(teacher_lesson_type)
    db.commit()
    db.refresh(teacher)

    return teacher


@router.delete("/lesson-types/{teacher_id}/{lesson_type_id}")
async def delete_teacher_lesson_type(
        teacher_id: uuid.UUID,
        lesson_type_id: uuid.UUID,
        response: Response,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).options().filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    lesson_type = db.query(models.LessonType).filter(models.LessonType.id == lesson_type_id).first()
    if not lesson_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Стиль танца не найден"
        )

    existing_lesson_type = db.query(models.TeacherLessonType).filter(
        models.TeacherLessonType.teacher_id == teacher_id,
        models.TeacherLessonType.lesson_type_id == lesson_type_id
    ).first()

    if not existing_lesson_type:
        response.status_code=status.HTTP_204_NO_CONTENT
        return "Преподаватель не связан с этим стилем танца"

    db.delete(existing_lesson_type)
    db.commit()

    return "Стиль танца преподавателя удалён успешно"


@router.post("/groups/{teacher_id}/{group_id}", response_model=schemas.TeacherFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_teacher_group(
        teacher_id: uuid.UUID,
        group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).options().filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    existing_group = db.query(models.TeacherGroup).filter(
        models.TeacherGroup.teacher_id == teacher_id,
        models.TeacherGroup.group_id == group_id
    ).first()

    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель уже связан с этой группой"
        )

    teacher_group = models.TeacherGroup(
        teacher_id=teacher_id,
        group_id=group_id
    )

    db.add(teacher_group)
    db.commit()
    db.refresh(teacher)

    return teacher


@router.delete("/groups/{teacher_id}/{group_id}")
async def delete_teacher_group(
        teacher_id: uuid.UUID,
        group_id: uuid.UUID,
        response: Response,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).options().filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    existing_group = db.query(models.TeacherGroup).filter(
        models.TeacherGroup.teacher_id == teacher_id,
        models.TeacherGroup.group_id == group_id
    ).first()

    if not existing_group:
        response.status_code = status.HTTP_204_NO_CONTENT
        return "Преподаватель не связан с этой группой"

    db.delete(existing_group)
    db.commit()

    return "Преподаватель успешно удалён из группы"


@router.post("/lessons/{teacher_id}/{lesson_id}", response_model=schemas.LessonFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_teacher_lesson(
        teacher_id: uuid.UUID,
        lesson_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).options().filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    existing_lesson = db.query(models.TeacherLesson).filter(
        models.TeacherLesson.teacher_id == teacher_id,
        models.TeacherLesson.lesson_id == lesson_id
    ).first()

    if existing_lesson:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель уже связан с этим занятием"
        )

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher_id,
        lesson_id=lesson_id
    )

    db.add(teacher_lesson)
    db.commit()
    db.refresh(lesson)

    return lesson


@router.delete("/lessons/{teacher_id}/{lesson_id}")
async def delete_teacher_lesson(
        teacher_id: uuid.UUID,
        lesson_id: uuid.UUID,
        response: Response,
        db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).options().filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    existing_lesson = db.query(models.TeacherLesson).filter(
        models.TeacherLesson.teacher_id == teacher_id,
        models.TeacherLesson.lesson_id == lesson_id
    ).first()

    if not existing_lesson:
        response.status_code = status.HTTP_204_NO_CONTENT
        return "Преподаватель не связан с этим занятием"

    db.delete(existing_lesson)
    db.commit()

    return "Преподаватель успешно удалён из занятия"
