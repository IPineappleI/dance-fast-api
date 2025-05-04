from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from pydantic import AfterValidator
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db, TIMEZONE
from app.routers.auth import patch_user
from app.models import User, Student, Level, Group, Lesson, Subscription, Payment
from app.models.association import *
from app.schemas.student import *

router = APIRouter(
    prefix='/students',
    tags=['students']
)


def apply_filters_to_students(students, filters, db):
    if filters.level_ids:
        students = students.where(Student.level_id.in_(filters.level_ids))

    if filters.group_ids:
        students = students.where(
            db.query(StudentGroup).where(
                StudentGroup.student_id == Student.id,
                StudentGroup.group_id.in_(filters.group_ids)
            ).exists()
        )

    if filters.terminated is not None:
        students = students.join(User).where(User.terminated == filters.terminated)

    return students


def check_order_by(order_by: str) -> str:
    assert order_by in ['created_at'], \
        'Данная сортировка невозможна'
    return order_by


@router.post('/search', response_model=StudentPage)
async def search_students(
        filters: StudentFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    students = db.query(Student)
    students = apply_filters_to_students(students, filters, db)
    return StudentPage(
        students=students.order_by(
            text('students.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=students.count()
    )


@router.post('/search/full-info', response_model=StudentFullInfoPage)
async def search_students_full_info(
        filters: StudentFilters,
        order_by: Annotated[str, AfterValidator(check_order_by)] = 'created_at',
        desc: bool = True,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=100)] = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    students = db.query(Student)
    students = apply_filters_to_students(students, filters, db)
    return StudentFullInfoPage(
        students=students.order_by(
            text('students.' + order_by + (' DESC' if desc else ''))
        ).offset(offset).limit(limit).all(),
        total=students.count()
    )


@router.get('/{student_id}', response_model=StudentInfo)
async def get_student_by_id(
        student_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ученик не найден'
        )
    return student


@router.get('/full-info/{student_id}', response_model=StudentFullInfo)
async def get_student_full_info_by_id(
        student_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ученик не найден'
        )
    return student


@router.patch('/{student_id}', response_model=StudentFullInfo)
async def patch_student(
        student_id: uuid.UUID,
        student_data: StudentUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == student_id).first()
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

    if student_data.level_id:
        level = db.query(Level).where(Level.id == student_data.level_id).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Уровень подготовки не найден'
            )
        if level.terminated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Уровень подготовки не активен'
            )
        student.level_id = student_data.level_id
        student_data.level_id = None

    if student_data.terminated:
        db.query(StudentGroup).where(StudentGroup.student_id == student_id).delete()

        db.query(LessonSubscription).where(
            LessonSubscription.cancelled == False,
            db.query(Subscription).where(
                Subscription.id == LessonSubscription.subscription_id,
                Subscription.student_id == student_id
            ).join(Lesson, Lesson.id == LessonSubscription.lesson_id).where(
                Lesson.start_time >= datetime.now(TIMEZONE)
            ).exists()
        ).update(
            {LessonSubscription.cancelled: True}
        )

    await patch_user(student.user_id, student_data, db)

    db.refresh(student)

    return student


def get_fitting_subscriptions(student, group, db):
    fitting_subscriptions = db.query(Subscription).join(Payment).where(
        Subscription.student_id == student.id,
        or_(
            Subscription.expiration_date == None,
            Subscription.expiration_date > datetime.now(TIMEZONE)
        ),
        Payment.terminated == False,
        ~db.query(Lesson).where(
            Lesson.group_id == group.id,
            Lesson.start_time > datetime.now(TIMEZONE),
            Lesson.terminated == False,
            Lesson.is_confirmed == True,
            ~Lesson.lesson_type_id.in_(Subscription.lesson_type_ids)
        ).exists()
    ).all()

    return fitting_subscriptions


@router.post('/groups/{student_id}/{group_id}', response_model=StudentFullInfo,
             status_code=status.HTTP_201_CREATED)
async def create_student_group(
        student_id: uuid.UUID,
        group_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == student_id).first()
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

    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )
    if group.terminated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не активна'
        )
    if len(group.student_groups) >= group.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В группе нет свободных мест'
        )

    existing_group = db.query(StudentGroup).where(
        StudentGroup.student_id == student_id,
        StudentGroup.group_id == group_id
    ).first()
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ученик уже связан с этой группой'
        )

    fitting_subscriptions = get_fitting_subscriptions(student, group, db)

    if len(fitting_subscriptions) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Для вступления в группу у ученика должны быть абонементы, подходящие для всех занятий группы'
        )

    student_group = StudentGroup(
        student_id=student_id,
        group_id=group_id
    )

    db.add(student_group)
    db.commit()
    db.refresh(student)

    return student


@router.delete('/groups/{student_id}/{group_id}')
async def delete_student_group(
        student_id: uuid.UUID,
        group_id: uuid.UUID,
        response: Response,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    student = db.query(Student).where(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ученик не найден'
        )

    group = db.query(Group).where(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не найдена'
        )
    if group.terminated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа не активна'
        )

    if not current_user.admin and current_user.id != student.user_id:
        if current_user.teacher:
            if current_user.teacher not in group.teachers:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Преподаватель не связан с этой группой'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав'
            )

    existing_group = db.query(StudentGroup).where(
        StudentGroup.student_id == student_id,
        StudentGroup.group_id == group_id
    ).first()
    if not existing_group:
        response.status_code = status.HTTP_204_NO_CONTENT
        return 'Ученик не связан с этой группой'

    db.query(LessonSubscription).where(
        LessonSubscription.cancelled == False,
        db.query(Subscription).where(
            Subscription.id == LessonSubscription.subscription_id,
            Subscription.student_id == student_id
        ).join(Lesson, Lesson.id == LessonSubscription.lesson_id).where(
            Lesson.group_id == group_id,
            Lesson.start_time >= datetime.now(TIMEZONE)
        ).exists()
    ).update(
        {LessonSubscription.cancelled: True}
    )

    db.delete(existing_group)
    db.commit()

    return 'Ученик успешно удалён из группы'
