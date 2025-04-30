from datetime import datetime, timedelta, time

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.password import get_password_hash
from app.database import get_db, TIMEZONE
from app.models import *

router = APIRouter(
    prefix='/test',
    tags=['test']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_test_data(db: Session = Depends(get_db)):
    user_admin = User(
        email='max@admin.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Максим',
        last_name='Исмаилов',
        middle_name='Джабраилович',
        description='54 года, Калуга',
        phone_number='81337133754'
    )
    db.add(user_admin)
    db.commit()

    admin = Admin(
        user_id=user_admin.id,
        created_at=user_admin.created_at
    )
    db.add(admin)
    db.commit()

    level_beginner = Level(
        name='Начинающий',
        description='Для тех, кто только начал постигать искусство танца'
    )
    db.add(level_beginner)
    db.commit()

    level_advanced = Level(
        name='Продвинутый',
        description='Для тех, кто уверенно чувствует себя в танце'
    )
    db.add(level_advanced)
    db.commit()

    user_beginner1 = User(
        email='beginner1@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Иван',
        last_name='Иванов',
        middle_name='Иванович',
        description='23 года, Тверь',
        phone_number='89991234567'
    )
    db.add(user_beginner1)
    db.commit()

    student_beginner1 = Student(
        user_id=user_beginner1.id,
        level_id=level_beginner.id,
        created_at=user_beginner1.created_at
    )
    db.add(student_beginner1)
    db.commit()

    user_beginner2 = User(
        email='beginner2@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Максим',
        last_name='Максимов',
        middle_name='Максимович',
        description='22 года, Москва',
        phone_number='88005553535'
    )
    db.add(user_beginner2)
    db.commit()

    student_beginner2 = Student(
        user_id=user_beginner2.id,
        level_id=level_beginner.id,
        created_at=user_beginner2.created_at
    )
    db.add(student_beginner2)
    db.commit()

    user_beginner3 = User(
        email='beginner3@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Пётр',
        last_name='Петров',
        middle_name='Петрович',
        phone_number='81234567891'
    )
    db.add(user_beginner3)
    db.commit()

    student_beginner3 = Student(
        user_id=user_beginner3.id,
        level_id=level_beginner.id,
        created_at=user_beginner3.created_at
    )
    db.add(student_beginner3)
    db.commit()

    user_beginner4 = User(
        email='beginner4@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Алексей',
        last_name='Алексеев',
        middle_name='Алексеевич',
        phone_number='81234567892'
    )
    db.add(user_beginner4)
    db.commit()

    student_beginner4 = Student(
        user_id=user_beginner4.id,
        level_id=level_beginner.id,
        created_at=user_beginner4.created_at
    )
    db.add(student_beginner4)
    db.commit()

    user_beginner5 = User(
        email='beginner5@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Андрей',
        last_name='Андреев',
        middle_name='Андреевич',
        phone_number='81234567893'
    )
    db.add(user_beginner5)
    db.commit()

    student_beginner5 = Student(
        user_id=user_beginner5.id,
        level_id=level_beginner.id,
        created_at=user_beginner5.created_at
    )
    db.add(student_beginner5)
    db.commit()

    user_beginner6 = User(
        email='beginner6@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Сара',
        last_name='Штайнберг',
        phone_number='81234567894'
    )
    db.add(user_beginner6)
    db.commit()

    student_beginner6 = Student(
        user_id=user_beginner6.id,
        level_id=level_beginner.id,
        created_at=user_beginner6.created_at
    )
    db.add(student_beginner6)
    db.commit()

    user_beginner7 = User(
        email='beginner7@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Анна',
        last_name='Яблочкина',
        middle_name='Олеговна',
        phone_number='81234567895'
    )
    db.add(user_beginner7)
    db.commit()

    student_beginner7 = Student(
        user_id=user_beginner7.id,
        level_id=level_beginner.id,
        created_at=user_beginner7.created_at
    )
    db.add(student_beginner7)
    db.commit()

    user_beginner8 = User(
        email='beginner8@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Анастасия',
        last_name='Зорина',
        middle_name='Макаровна',
        phone_number='81234567896'
    )
    db.add(user_beginner8)
    db.commit()

    student_beginner8 = Student(
        user_id=user_beginner8.id,
        level_id=level_beginner.id,
        created_at=user_beginner8.created_at
    )
    db.add(student_beginner8)
    db.commit()

    user_beginner9 = User(
        email='beginner9@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Мария',
        last_name='Городовая',
        middle_name='Сергеевна',
        phone_number='81234567897'
    )
    db.add(user_beginner9)
    db.commit()

    student_beginner9 = Student(
        user_id=user_beginner9.id,
        level_id=level_beginner.id,
        created_at=user_beginner9.created_at
    )
    db.add(student_beginner9)
    db.commit()

    user_beginner10 = User(
        email='beginner10@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Антонина',
        last_name='Пушкина',
        middle_name='Арсениевна',
        phone_number='81234567898'
    )
    db.add(user_beginner10)
    db.commit()

    student_beginner10 = Student(
        user_id=user_beginner10.id,
        level_id=level_beginner.id,
        created_at=user_beginner10.created_at
    )
    db.add(student_beginner10)
    db.commit()

    user_advanced1 = User(
        email='advanced1@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Аристарх',
        last_name='Свирилов',
        middle_name='Архипович',
        description='30 лет, Екатеринбург',
        phone_number='81234567890'
    )
    db.add(user_advanced1)
    db.commit()

    student_advanced1 = Student(
        user_id=user_advanced1.id,
        level_id=level_advanced.id,
        created_at=user_advanced1.created_at
    )
    db.add(student_advanced1)
    db.commit()

    user_advanced2 = User(
        email='advanced2@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Елена',
        last_name='Марьина',
        middle_name='Дмитриевна',
        description='35 лет, Екатеринбург',
        phone_number='89876543211'
    )
    db.add(user_advanced2)
    db.commit()

    student_advanced2 = Student(
        user_id=user_advanced2.id,
        level_id=level_advanced.id,
        created_at=user_advanced2.created_at
    )
    db.add(student_advanced2)
    db.commit()

    user_advanced3 = User(
        email='advanced3@student.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Михаил',
        last_name='Наумов',
        middle_name='Владимирович',
        description='29 лет, Москва',
        phone_number='89876543212'
    )
    db.add(user_advanced3)
    db.commit()

    student_advanced3 = Student(
        user_id=user_advanced3.id,
        level_id=level_advanced.id,
        created_at=user_advanced3.created_at
    )
    db.add(student_advanced3)
    db.commit()

    user_teacher1 = User(
        email='teacher@teacher.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Семён',
        last_name='Павлов',
        middle_name='Семёнович',
        description='31 год, Самара',
        phone_number='89876543210'
    )
    db.add(user_teacher1)
    db.commit()

    teacher1 = Teacher(
        user_id=user_teacher1.id,
        created_at=user_teacher1.created_at
    )
    db.add(teacher1)
    db.commit()

    user_teacher2 = User(
        email='teacher2@teacher.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Ульяна',
        last_name='Полейко',
        middle_name='Михайловна',
        description='34 года, Курск',
        phone_number='89876543213'
    )
    db.add(user_teacher2)
    db.commit()

    teacher2 = Teacher(
        user_id=user_teacher2.id,
        created_at=user_teacher2.created_at
    )
    db.add(teacher2)
    db.commit()

    user_teacher3 = User(
        email='teacher3@teacher.com',
        hashed_password=get_password_hash('12345678'),
        first_name='Станислав',
        last_name='Филиппов',
        middle_name='Ильич',
        description='27 лет, Мытищи',
        phone_number='89876543214'
    )
    db.add(user_teacher3)
    db.commit()

    teacher3 = Teacher(
        user_id=user_teacher3.id,
        created_at=user_teacher3.created_at
    )
    db.add(teacher3)
    db.commit()

    group_beginner_tango = Group(
        name='Танго для начинающих',
        description='Для тех, кто хочет начать погружение в мир танго',
        level_id=level_beginner.id,
        max_capacity=12
    )
    db.add(group_beginner_tango)
    db.commit()

    group_beginner_hiphop = Group(
        name='Хип-хоп для начинающих',
        description='Для тех, кто хочет научиться танцевать в стиле хип-хоп',
        level_id=level_beginner.id,
        max_capacity=10
    )
    db.add(group_beginner_hiphop)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner1.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner6.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner2.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner7.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner3.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner8.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner1.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner4.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner5.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner9.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = StudentGroup(
        student_id=student_beginner10.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    teacher_group = TeacherGroup(
        teacher_id=teacher1.id,
        group_id=group_beginner_tango.id
    )
    db.add(teacher_group)
    db.commit()

    teacher_group = TeacherGroup(
        teacher_id=teacher2.id,
        group_id=group_beginner_tango.id
    )
    db.add(teacher_group)
    db.commit()

    teacher_group = TeacherGroup(
        teacher_id=teacher3.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(teacher_group)
    db.commit()

    dance_style_tango = DanceStyle(
        name='Танго',
        description='Танго - основной стиль танца нашей школы'
    )
    db.add(dance_style_tango)
    db.commit()

    dance_style_hiphop = DanceStyle(
        name='Хип-хоп',
        description='Более современный и активный стиль танца'
    )
    db.add(dance_style_hiphop)
    db.commit()

    lesson_type_tango_group = LessonType(
        dance_style_id=dance_style_tango.id,
        is_group=True
    )
    db.add(lesson_type_tango_group)
    db.commit()

    lesson_type_tango_pair = LessonType(
        dance_style_id=dance_style_tango.id,
        is_group=False
    )
    db.add(lesson_type_tango_pair)
    db.commit()

    lesson_type_hiphop_group = LessonType(
        dance_style_id=dance_style_hiphop.id,
        is_group=True
    )
    db.add(lesson_type_hiphop_group)
    db.commit()

    lesson_type_hiphop_indiv = LessonType(
        dance_style_id=dance_style_hiphop.id,
        is_group=False
    )
    db.add(lesson_type_hiphop_indiv)
    db.commit()

    teacher_lesson_type = TeacherLessonType(
        teacher_id=teacher1.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = TeacherLessonType(
        teacher_id=teacher1.id,
        lesson_type_id=lesson_type_tango_pair.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = TeacherLessonType(
        teacher_id=teacher2.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = TeacherLessonType(
        teacher_id=teacher2.id,
        lesson_type_id=lesson_type_hiphop_indiv.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = TeacherLessonType(
        teacher_id=teacher3.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    subscription_template_group1 = SubscriptionTemplate(
        name='4 групповых занятия',
        description='Наш самый популярный абонемент',
        lesson_count=4,
        price=8000
    )
    db.add(subscription_template_group1)
    db.commit()

    subscription_template_group2 = SubscriptionTemplate(
        name='8 групповых занятий',
        description='Выгодно!',
        lesson_count=8,
        price=15000
    )
    db.add(subscription_template_group2)
    db.commit()

    subscription_template_group3 = SubscriptionTemplate(
        name='12 групповых занятий',
        description='Временное предложение!',
        lesson_count=12,
        expiration_date=datetime.now(TIMEZONE) + timedelta(days=14),
        expiration_day_count=14,
        price=21000
    )
    db.add(subscription_template_group3)
    db.commit()

    subscription_template_indiv = SubscriptionTemplate(
        name='Индивидуальное занятие',
        lesson_count=1,
        price=3500
    )
    db.add(subscription_template_indiv)
    db.commit()

    subscription_template_indiv4 = SubscriptionTemplate(
        name='4 индивидуальных занятия',
        lesson_count=4,
        price=12000
    )
    db.add(subscription_template_indiv4)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_group1.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_group1.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_group2.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_group2.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_group3.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_group3.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_indiv.id,
        lesson_type_id=lesson_type_tango_pair.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_indiv.id,
        lesson_type_id=lesson_type_hiphop_indiv.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_indiv4.id,
        lesson_type_id=lesson_type_tango_pair.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = SubscriptionLessonType(
        subscription_template_id=subscription_template_indiv4.id,
        lesson_type_id=lesson_type_hiphop_indiv.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    payment_type_card = PaymentType(
        name='Картой'
    )
    db.add(payment_type_card)
    db.commit()

    payment_type_cash = PaymentType(
        name='Наличными'
    )
    db.add(payment_type_cash)
    db.commit()

    payment0 = Payment(
        payment_type_id=payment_type_cash.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=14)
    )
    db.add(payment0)
    db.commit()

    subscription0 = Subscription(
        student_id=student_beginner1.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment0.id
    )
    db.add(subscription0)
    db.commit()

    payment1 = Payment(
        payment_type_id=payment_type_card.id,
        details='Оплата прошла успешно',
        created_at=datetime.now(TIMEZONE) - timedelta(days=1)
    )
    db.add(payment1)
    db.commit()

    subscription1 = Subscription(
        student_id=student_beginner1.id,
        subscription_template_id=subscription_template_group3.id,
        expiration_date=datetime.now(TIMEZONE) + timedelta(days=14),
        payment_id=payment1.id
    )
    db.add(subscription1)
    db.commit()

    payment2 = Payment(
        payment_type_id=payment_type_card.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=8)
    )
    db.add(payment2)
    db.commit()

    subscription2 = Subscription(
        student_id=student_beginner2.id,
        subscription_template_id=subscription_template_group2.id,
        payment_id=payment2.id
    )
    db.add(subscription2)
    db.commit()

    payment3 = Payment(
        payment_type_id=payment_type_cash.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=7)
    )
    db.add(payment3)
    db.commit()

    subscription3 = Subscription(
        student_id=student_beginner3.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment3.id
    )
    db.add(subscription3)
    db.commit()

    payment4 = Payment(
        payment_type_id=payment_type_card.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=5)
    )
    db.add(payment4)
    db.commit()

    subscription4 = Subscription(
        student_id=student_beginner4.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment4.id
    )
    db.add(subscription4)
    db.commit()

    payment5 = Payment(
        payment_type_id=payment_type_card.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=5)
    )
    db.add(payment5)
    db.commit()

    subscription5 = Subscription(
        student_id=student_beginner5.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment5.id
    )
    db.add(subscription5)
    db.commit()

    payment6 = Payment(
        payment_type_id=payment_type_cash.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=4)
    )
    db.add(payment6)
    db.commit()

    subscription6 = Subscription(
        student_id=student_beginner6.id,
        subscription_template_id=subscription_template_group2.id,
        payment_id=payment6.id
    )
    db.add(subscription6)
    db.commit()

    payment7 = Payment(
        payment_type_id=payment_type_card.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=2)
    )
    db.add(payment7)
    db.commit()

    subscription7 = Subscription(
        student_id=student_beginner7.id,
        subscription_template_id=subscription_template_group2.id,
        payment_id=payment7.id
    )
    db.add(subscription7)
    db.commit()

    payment8 = Payment(
        payment_type_id=payment_type_cash.id,
        created_at=datetime.now(TIMEZONE) - timedelta(days=2)
    )
    db.add(payment8)
    db.commit()

    subscription8 = Subscription(
        student_id=student_beginner8.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment8.id
    )
    db.add(subscription8)
    db.commit()

    payment9 = Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment9)
    db.commit()

    subscription9 = Subscription(
        student_id=student_beginner9.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment9.id
    )
    db.add(subscription9)
    db.commit()

    payment10 = Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment10)
    db.commit()

    subscription10 = Subscription(
        student_id=student_beginner10.id,
        subscription_template_id=subscription_template_group3.id,
        payment_id=payment10.id
    )
    db.add(subscription10)
    db.commit()

    payment11 = Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment11)
    db.commit()

    subscription11 = Subscription(
        student_id=student_advanced1.id,
        subscription_template_id=subscription_template_indiv4.id,
        payment_id=payment11.id
    )
    db.add(subscription11)
    db.commit()

    payment12 = Payment(
        payment_type_id=payment_type_cash.id
    )
    db.add(payment12)
    db.commit()

    subscription12 = Subscription(
        student_id=student_advanced3.id,
        subscription_template_id=subscription_template_indiv4.id,
        payment_id=payment12.id
    )
    db.add(subscription12)
    db.commit()

    subscription13 = Subscription(
        student_id=student_advanced2.id,
        subscription_template_id=subscription_template_indiv.id
    )
    db.add(subscription13)
    db.commit()

    subscription14 = Subscription(
        student_id=student_advanced2.id,
        subscription_template_id=subscription_template_indiv.id
    )
    db.add(subscription14)
    db.commit()

    subscription15 = Subscription(
        student_id=student_advanced3.id,
        subscription_template_id=subscription_template_indiv.id
    )
    db.add(subscription15)
    db.commit()

    classroom1 = Classroom(
        name='Зал 101',
        description='Наш любимый зал'
    )
    db.add(classroom1)
    db.commit()

    classroom2 = Classroom(
        name='Зал 102'
    )
    db.add(classroom2)
    db.commit()

    classroom3 = Classroom(
        name='Зал 201'
    )
    db.add(classroom3)
    db.commit()

    classroom4 = Classroom(
        name='Зал 202'
    )
    db.add(classroom4)
    db.commit()

    lesson1 = Lesson(
        name='Танго. Введение',
        description='Постигаем азы танго',
        lesson_type_id=lesson_type_tango_group.id,
        start_time=datetime.now(TIMEZONE) - timedelta(days=7),
        finish_time=datetime.now(TIMEZONE) - timedelta(days=7) + timedelta(minutes=90),
        classroom_id=classroom1.id,
        group_id=group_beginner_tango.id,
        are_neighbours_allowed=False,
        is_confirmed=True
    )
    db.add(lesson1)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson1.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription2.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription7.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription3.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription8.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson2 = Lesson(
        name='Групповое занятие по танго',
        lesson_type_id=lesson_type_tango_group.id,
        start_time=datetime.now(TIMEZONE),
        finish_time=datetime.now(TIMEZONE) + timedelta(minutes=90),
        classroom_id=classroom2.id,
        group_id=group_beginner_tango.id,
        are_neighbours_allowed=False,
        is_confirmed=True
    )
    db.add(lesson2)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson2.id
    )
    db.add(teacher_lesson)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson2.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription6.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription2.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription7.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription3.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription8.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson3 = Lesson(
        name='Групповое занятие по танго',
        lesson_type_id=lesson_type_tango_group.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=7),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=7) + timedelta(minutes=90),
        classroom_id=classroom2.id,
        group_id=group_beginner_tango.id,
        are_neighbours_allowed=False,
        is_confirmed=True
    )
    db.add(lesson3)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson3.id
    )
    db.add(teacher_lesson)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson3.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription6.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription2.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription7.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription3.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription8.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson4 = Lesson(
        name='Групповое занятие по хип-хопу',
        lesson_type_id=lesson_type_hiphop_group.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=2),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=2) + timedelta(minutes=90),
        classroom_id=classroom4.id,
        group_id=group_beginner_hiphop.id,
        are_neighbours_allowed=True,
        is_confirmed=True
    )
    db.add(lesson4)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher3.id,
        lesson_id=lesson4.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription4.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription5.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription9.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription10.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson5 = Lesson(
        name='Групповое занятие по хип-хопу',
        lesson_type_id=lesson_type_hiphop_group.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=9),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=9) + timedelta(minutes=90),
        classroom_id=classroom4.id,
        group_id=group_beginner_hiphop.id,
        are_neighbours_allowed=True,
        is_confirmed=True
    )
    db.add(lesson5)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher3.id,
        lesson_id=lesson5.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription4.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription5.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription9.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription10.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson6 = Lesson(
        name='Индивидуальное занятие по танго в паре',
        lesson_type_id=lesson_type_tango_pair.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=1),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=1) + timedelta(minutes=60),
        classroom_id=classroom3.id,
        are_neighbours_allowed=False,
        is_confirmed=True
    )
    db.add(lesson6)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson6.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription11.id,
        lesson_id=lesson6.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson7 = Lesson(
        name='Индивидуальное занятие по хип-хопу',
        lesson_type_id=lesson_type_hiphop_indiv.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=9) + timedelta(minutes=15),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=9) + timedelta(minutes=75),
        classroom_id=classroom4.id,
        are_neighbours_allowed=True,
        is_confirmed=True
    )
    db.add(lesson7)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson7.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription12.id,
        lesson_id=lesson7.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson8 = Lesson(
        name='Заявка на индивидуальное занятие по танго',
        lesson_type_id=lesson_type_tango_pair.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=11),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=11) + timedelta(minutes=60),
        are_neighbours_allowed=True,
        is_confirmed=False
    )
    db.add(lesson8)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson8.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription13.id,
        lesson_id=lesson8.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson9 = Lesson(
        name='Заявка на индивидуальное занятие по хип-хопу',
        lesson_type_id=lesson_type_hiphop_indiv.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=3) + timedelta(minutes=9),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=3) + timedelta(minutes=69),
        are_neighbours_allowed=True,
        is_confirmed=False
    )
    db.add(lesson9)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson9.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription14.id,
        lesson_id=lesson9.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson10 = Lesson(
        name='Заявка на индивидуальное занятие по хип-хопу',
        lesson_type_id=lesson_type_hiphop_indiv.id,
        start_time=datetime.now(TIMEZONE) + timedelta(days=13),
        finish_time=datetime.now(TIMEZONE) + timedelta(days=13) + timedelta(minutes=50),
        are_neighbours_allowed=False,
        is_confirmed=False
    )
    db.add(lesson10)
    db.commit()

    teacher_lesson = TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson10.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = LessonSubscription(
        subscription_id=subscription15.id,
        lesson_id=lesson10.id
    )
    db.add(lesson_subscription)
    db.commit()

    event_type1 = EventType(
        name='Лекция',
        description='Информативная и интересная лекция со свободным посещением'
    )
    db.add(event_type1)
    db.commit()

    event_type2 = EventType(
        name='Праздник'
    )
    db.add(event_type2)
    db.commit()

    event1 = Event(
        event_type_id=event_type1.id,
        name='Лекция по истории танго',
        description='Безумно захватывающая лекция!',
        start_time=datetime.now(TIMEZONE) + timedelta(minutes=100)
    )
    db.add(event1)
    db.commit()

    event2 = Event(
        event_type_id=event_type1.id,
        name='Лекция по истории хип-хопа',
        start_time=datetime.now(TIMEZONE) + timedelta(days=10)
    )
    db.add(event2)
    db.commit()

    event3 = Event(
        event_type_id=event_type2.id,
        name='Юбилей Elcentro',
        start_time=datetime.now(TIMEZONE) + timedelta(days=14)
    )
    db.add(event3)
    db.commit()

    slot1 = Slot(
        teacher_id=teacher1.id,
        day_of_week=1,
        start_time=time(16, 0, 0, 0, TIMEZONE),
        end_time=time(17, 0, 0, 0, TIMEZONE)
    )
    db.add(slot1)
    db.commit()

    slot2 = Slot(
        teacher_id=teacher2.id,
        day_of_week=2,
        start_time=time(18, 0, 0, 0, TIMEZONE),
        end_time=time(19, 0, 0, 0, TIMEZONE)
    )
    db.add(slot2)
    db.commit()

    slot3 = Slot(
        teacher_id=teacher2.id,
        day_of_week=4,
        start_time=time(18, 0, 0, 0, TIMEZONE),
        end_time=time(19, 0, 0, 0, TIMEZONE)
    )
    db.add(slot3)
    db.commit()

    return 'Тестовые данные созданы успешно'
