import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import exists
from sqlalchemy.orm import Session
from typing import List

from app.auth.jwt import get_current_admin, get_current_user
from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Группа не найдена"}}
)


@router.post("/", response_model=schemas.GroupInfo, status_code=status.HTTP_201_CREATED)
async def create_group(
        group_data: schemas.GroupBase,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    if group_data.max_capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество мест в группе должно быть положительным"
        )

    level = db.query(models.Level).filter(models.Level.id == group_data.level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уровень подготовки не найден"
        )
    if level.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Уровень подготовки не активен"
        )

    group = models.Group(
        name=group_data.name,
        description=group_data.description,
        max_capacity=group_data.max_capacity,
        level_id=group_data.level_id
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return group


def apply_filters_to_groups(groups: Query, filters):
    if type(filters.has_teachers) is bool:
        groups = groups.filter((exists(models.TeacherGroup).where(
            models.TeacherGroup.group_id == models.Group.id
        )) == filters.has_teachers)
    if filters.teacher_ids:
        groups = groups.join(models.TeacherGroup).filter(models.TeacherGroup.teacher_id.in_(filters.teacher_ids))

    if type(filters.has_students) is bool:
        groups = groups.filter((exists(models.StudentGroup).where(
            models.StudentGroup.group_id == models.Group.id
        )) == filters.has_students)
    if filters.student_ids:
        groups = groups.join(models.StudentGroup).filter(models.StudentGroup.student_id.in_(filters.student_ids))

    if type(filters.terminated) is bool:
        groups = groups.filter(models.Event.terminated == filters.terminated)

    if filters.dance_style_ids:
        groups = groups.join(models.Lesson).join(models.LessonType).filter(
            models.LessonType.dance_style_id.in_(filters.dance_style_ids)
        )

    if filters.level_ids:
        groups = groups.filter(models.Group.level_id.in_(filters.level_ids))

    return groups


@router.post("/search", response_model=List[schemas.GroupInfo])
async def search_groups(
        filters: schemas.GroupSearch,
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    groups = db.query(models.Group)
    groups = apply_filters_to_groups(groups, filters)
    groups = groups.offset(skip).limit(limit).all()
    return groups


@router.post("/search/full-info", response_model=List[schemas.GroupFullInfo])
async def search_groups_full_info(
        filters: schemas.GroupSearch,
        skip: int = 0, limit: int = 100,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    groups = db.query(models.Group)
    groups = apply_filters_to_groups(groups, filters)
    groups = groups.offset(skip).limit(limit).all()
    return groups


@router.get("/{group_id}", response_model=schemas.GroupInfo)
async def get_group_by_id(
        group_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    return group


@router.get("/full-info/{group_id}", response_model=schemas.GroupFullInfo)
async def get_group_full_info_by_id(
        group_id: uuid.UUID,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    return group


@router.patch("/{group_id}", response_model=schemas.GroupFullInfo, status_code=status.HTTP_200_OK)
async def patch_group(
        group_id: uuid.UUID,
        group_data: schemas.GroupUpdate,
        current_admin: models.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )

    if group_data.max_capacity is not None and group_data.max_capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество мест в группе должно быть положительным"
        )

    if group_data.level_id:
        level = db.query(models.Level).filter(models.Level.id == group_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уровень подготовки не найден"
            )
        if level.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Уровень подготовки не активен"
            )

    for field, value in group_data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    return group
