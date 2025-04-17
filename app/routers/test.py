from datetime import datetime, timezone, timedelta, time

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.password import get_password_hash
from app.database import get_db
from app import models


router = APIRouter(
    prefix="/test",
    tags=["test"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_test_data(db: Session = Depends(get_db)):
    user_admin = models.User(
        email="max@admin.com",
        hashed_password=get_password_hash("13371337"),
        first_name="Максим",
        last_name="Исмаилов",
        middle_name="Джабраилович",
        description="54 года, Калуга",
        phone_number="81337133754"
    )
    db.add(user_admin)
    db.commit()

    admin = models.Admin(
        user_id=user_admin.id,
        created_at=user_admin.created_at
    )
    db.add(admin)
    db.commit()

    level_beginner = models.Level(
        name="Начинающий",
        description="Для тех, кто только начал постигать искусство танца"
    )
    db.add(level_beginner)
    db.commit()

    level_advanced = models.Level(
        name="Продвинутый",
        description="Для тех, кто уверенно чувствует себя в танце"
    )
    db.add(level_advanced)
    db.commit()

    user_beginner1 = models.User(
        email="beginner1@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Иван",
        last_name="Иванов",
        middle_name="Иванович",
        description="23 года, Тверь",
        phone_number="89991234567"
    )
    db.add(user_beginner1)
    db.commit()

    student_beginner1 = models.Student(
        user_id=user_beginner1.id,
        level_id=level_beginner.id,
        created_at=user_beginner1.created_at
    )
    db.add(student_beginner1)
    db.commit()

    user_beginner2 = models.User(
        email="beginner2@student.com",
        hashed_password=get_password_hash("87654321"),
        first_name="Максим",
        last_name="Максимов",
        middle_name="Максимович",
        description="22 года, Москва",
        phone_number="88005553535"
    )
    db.add(user_beginner2)
    db.commit()

    student_beginner2 = models.Student(
        user_id=user_beginner2.id,
        level_id=level_beginner.id,
        created_at=user_beginner2.created_at
    )
    db.add(student_beginner2)
    db.commit()

    user_beginner3 = models.User(
        email="beginner3@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Пётр",
        last_name="Петров",
        middle_name="Петрович",
        phone_number="81234567891"
    )
    db.add(user_beginner3)
    db.commit()

    student_beginner3 = models.Student(
        user_id=user_beginner3.id,
        level_id=level_beginner.id,
        created_at=user_beginner3.created_at
    )
    db.add(student_beginner3)
    db.commit()

    user_beginner4 = models.User(
        email="beginner4@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Алексей",
        last_name="Алексеев",
        middle_name="Алексеевич",
        phone_number="81234567892"
    )
    db.add(user_beginner4)
    db.commit()

    student_beginner4 = models.Student(
        user_id=user_beginner4.id,
        level_id=level_beginner.id,
        created_at=user_beginner4.created_at
    )
    db.add(student_beginner4)
    db.commit()

    user_beginner5 = models.User(
        email="beginner5@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Андрей",
        last_name="Андреев",
        middle_name="Андреевич",
        phone_number="81234567893"
    )
    db.add(user_beginner5)
    db.commit()

    student_beginner5 = models.Student(
        user_id=user_beginner5.id,
        level_id=level_beginner.id,
        created_at=user_beginner5.created_at
    )
    db.add(student_beginner5)
    db.commit()

    user_beginner6 = models.User(
        email="beginner6@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Сара",
        last_name="Штайнберг",
        phone_number="81234567894"
    )
    db.add(user_beginner6)
    db.commit()

    student_beginner6 = models.Student(
        user_id=user_beginner6.id,
        level_id=level_beginner.id,
        created_at=user_beginner6.created_at
    )
    db.add(student_beginner6)
    db.commit()

    user_beginner7 = models.User(
        email="beginner7@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Анна",
        last_name="Яблочкина",
        middle_name="Олеговна",
        phone_number="81234567895"
    )
    db.add(user_beginner7)
    db.commit()

    student_beginner7 = models.Student(
        user_id=user_beginner7.id,
        level_id=level_beginner.id,
        created_at=user_beginner7.created_at
    )
    db.add(student_beginner7)
    db.commit()

    user_beginner8 = models.User(
        email="beginner8@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Анастасия",
        last_name="Зорина",
        middle_name="Макаровна",
        phone_number="81234567896"
    )
    db.add(user_beginner8)
    db.commit()

    student_beginner8 = models.Student(
        user_id=user_beginner8.id,
        level_id=level_beginner.id,
        created_at=user_beginner8.created_at
    )
    db.add(student_beginner8)
    db.commit()

    user_beginner9 = models.User(
        email="beginner9@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Мария",
        last_name="Городовая",
        middle_name="Сергеевна",
        phone_number="81234567897"
    )
    db.add(user_beginner9)
    db.commit()

    student_beginner9 = models.Student(
        user_id=user_beginner9.id,
        level_id=level_beginner.id,
        created_at=user_beginner9.created_at
    )
    db.add(student_beginner9)
    db.commit()

    user_beginner10 = models.User(
        email="beginner10@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Антонина",
        last_name="Пушкина",
        middle_name="Арсениевна",
        phone_number="81234567898"
    )
    db.add(user_beginner10)
    db.commit()

    student_beginner10 = models.Student(
        user_id=user_beginner10.id,
        level_id=level_beginner.id,
        created_at=user_beginner10.created_at
    )
    db.add(student_beginner10)
    db.commit()

    user_advanced1 = models.User(
        email="advanced1@student.com",
        hashed_password=get_password_hash("42424242"),
        first_name="Аристарх",
        last_name="Свирилов",
        middle_name="Архипович",
        description="30 лет, Екатеринбург",
        phone_number="81234567890"
    )
    db.add(user_advanced1)
    db.commit()

    student_advanced1 = models.Student(
        user_id=user_advanced1.id,
        level_id=level_advanced.id,
        created_at=user_advanced1.created_at
    )
    db.add(student_advanced1)
    db.commit()

    user_advanced2 = models.User(
        email="advanced2@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Елена",
        last_name="Марьина",
        middle_name="Дмитриевна",
        description="35 лет, Екатеринбург",
        phone_number="89876543211"
    )
    db.add(user_advanced2)
    db.commit()

    student_advanced2 = models.Student(
        user_id=user_advanced2.id,
        level_id=level_advanced.id,
        created_at=user_advanced2.created_at
    )
    db.add(student_advanced2)
    db.commit()

    user_advanced3 = models.User(
        email="advanced3@student.com",
        hashed_password=get_password_hash("12345678"),
        first_name="Михаил",
        last_name="Наумов",
        middle_name="Владимирович",
        description="29 лет, Москва",
        phone_number="89876543212"
    )
    db.add(user_advanced3)
    db.commit()

    student_advanced3 = models.Student(
        user_id=user_advanced3.id,
        level_id=level_advanced.id,
        created_at=user_advanced3.created_at
    )
    db.add(student_advanced3)
    db.commit()

    user_teacher1 = models.User(
        email="teacher@teacher.com",
        hashed_password=get_password_hash("semensemenych"),
        first_name="Семён",
        last_name="Павлов",
        middle_name="Семёнович",
        description="31 год, Самара",
        phone_number="89876543210"
    )
    db.add(user_teacher1)
    db.commit()

    teacher1 = models.Teacher(
        user_id=user_teacher1.id,
        created_at=user_teacher1.created_at
    )
    db.add(teacher1)
    db.commit()

    user_teacher2 = models.User(
        email="teacher2@teacher.com",
        hashed_password=get_password_hash("password123"),
        first_name="Ульяна",
        last_name="Полейко",
        middle_name="Михайловна",
        description="34 года, Курск",
        phone_number="89876543213"
    )
    db.add(user_teacher2)
    db.commit()

    teacher2 = models.Teacher(
        user_id=user_teacher2.id,
        created_at=user_teacher2.created_at
    )
    db.add(teacher2)
    db.commit()

    user_teacher3 = models.User(
        email="teacher3@teacher.com",
        hashed_password=get_password_hash("underground"),
        first_name="Станислав",
        last_name="Филиппов",
        middle_name="Ильич",
        description="27 лет, Мытищи",
        phone_number="89876543214"
    )
    db.add(user_teacher3)
    db.commit()

    teacher3 = models.Teacher(
        user_id=user_teacher3.id,
        created_at=user_teacher3.created_at
    )
    db.add(teacher3)
    db.commit()

    group_beginner_tango = models.Group(
        name="Танго для начинающих",
        description="Для тех, кто хочет начать погружение в мир танго",
        level_id=level_beginner.id,
        max_capacity=12
    )
    db.add(group_beginner_tango)
    db.commit()

    group_advanced_tango = models.Group(
        name="Танго. Индивидуальные занятия в паре. Продвинутый уровень",
        level_id=level_advanced.id,
        max_capacity=1
    )
    db.add(group_advanced_tango)
    db.commit()

    group_beginner_hiphop = models.Group(
        name="Хип-хоп для начинающих",
        description="Для тех, кто хочет научиться танцевать в стиле хип-хоп",
        level_id=level_beginner.id,
        max_capacity=10
    )
    db.add(group_beginner_hiphop)
    db.commit()

    group_advanced_hiphop = models.Group(
        name="Хип-хоп. Индивидуальные занятия. Продвинутый уровень",
        level_id=level_advanced.id,
        max_capacity=1
    )
    db.add(group_advanced_hiphop)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner1.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner6.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner2.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner7.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner3.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner8.id,
        group_id=group_beginner_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner1.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner4.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner5.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner9.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_beginner10.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_advanced1.id,
        group_id=group_advanced_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_advanced2.id,
        group_id=group_advanced_tango.id
    )
    db.add(student_group)
    db.commit()

    student_group = models.StudentGroup(
        student_id=student_advanced3.id,
        group_id=group_advanced_hiphop.id
    )
    db.add(student_group)
    db.commit()

    teacher_group = models.TeacherGroup(
        teacher_id=teacher1.id,
        group_id=group_beginner_tango.id
    )
    db.add(teacher_group)
    db.commit()

    teacher_group = models.TeacherGroup(
        teacher_id=teacher2.id,
        group_id=group_beginner_tango.id
    )
    db.add(teacher_group)
    db.commit()

    teacher_group = models.TeacherGroup(
        teacher_id=teacher1.id,
        group_id=group_advanced_tango.id
    )
    db.add(teacher_group)
    db.commit()

    teacher_group = models.TeacherGroup(
        teacher_id=teacher2.id,
        group_id=group_advanced_hiphop.id
    )
    db.add(teacher_group)
    db.commit()

    teacher_group = models.TeacherGroup(
        teacher_id=teacher3.id,
        group_id=group_beginner_hiphop.id
    )
    db.add(teacher_group)
    db.commit()

    lesson_type_tango_group = models.LessonType(
        name="Групповые занятия по танго",
        description="Танго - основной стиль танца нашей школы"
    )
    db.add(lesson_type_tango_group)
    db.commit()

    lesson_type_tango_pair = models.LessonType(
        name="Индивидуальные занятия по танго в паре"
    )
    db.add(lesson_type_tango_pair)
    db.commit()

    lesson_type_hiphop_group = models.LessonType(
        name="Групповые занятия по хип-хопу",
        description="Более современный и активный стиль танца"
    )
    db.add(lesson_type_hiphop_group)
    db.commit()

    lesson_type_hiphop_indiv = models.LessonType(
        name="Индивидуальные занятия по хип-хопу"
    )
    db.add(lesson_type_hiphop_indiv)
    db.commit()

    teacher_lesson_type = models.TeacherLessonType(
        teacher_id=teacher1.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = models.TeacherLessonType(
        teacher_id=teacher1.id,
        lesson_type_id=lesson_type_tango_pair.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = models.TeacherLessonType(
        teacher_id=teacher2.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = models.TeacherLessonType(
        teacher_id=teacher2.id,
        lesson_type_id=lesson_type_hiphop_indiv.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    teacher_lesson_type = models.TeacherLessonType(
        teacher_id=teacher3.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(teacher_lesson_type)
    db.commit()

    subscription_template_group1 = models.SubscriptionTemplate(
        name="4 групповых занятия",
        description="Наш самый популярный абонемент",
        lesson_count=4,
        price=8000
    )
    db.add(subscription_template_group1)
    db.commit()

    subscription_template_group2 = models.SubscriptionTemplate(
        name="8 групповых занятий",
        description="Выгодно!",
        lesson_count=8,
        price=15000
    )
    db.add(subscription_template_group2)
    db.commit()

    subscription_template_group3 = models.SubscriptionTemplate(
        name="12 групповых занятий",
        description="Временное предложение!",
        lesson_count=12,
        expiration_date=datetime.now(timezone.utc) + timedelta(days=14),
        expiration_day_count=14,
        price=21000
    )
    db.add(subscription_template_group3)
    db.commit()

    subscription_template_indiv = models.SubscriptionTemplate(
        name="4 индивидуальных занятия",
        lesson_count=4,
        price=12000
    )
    db.add(subscription_template_indiv)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_group1.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_group1.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_group2.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_group2.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_group3.id,
        lesson_type_id=lesson_type_tango_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_group3.id,
        lesson_type_id=lesson_type_hiphop_group.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_indiv.id,
        lesson_type_id=lesson_type_tango_pair.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    subscription_lesson_type = models.SubscriptionLessonType(
        subscription_template_id=subscription_template_indiv.id,
        lesson_type_id=lesson_type_hiphop_indiv.id
    )
    db.add(subscription_lesson_type)
    db.commit()

    payment_type_card = models.PaymentType(
        name="Картой"
    )
    db.add(payment_type_card)
    db.commit()

    payment_type_cash = models.PaymentType(
        name="Наличными"
    )
    db.add(payment_type_cash)
    db.commit()

    payment1 = models.Payment(
        payment_type_id=payment_type_card.id,
        details="Оплата прошла успешно"
    )
    db.add(payment1)
    db.commit()

    subscription1 = models.Subscription(
        student_id=student_beginner1.id,
        subscription_template_id=subscription_template_group3.id,
        expiration_date=datetime.now(timezone.utc) + timedelta(days=14),
        payment_id=payment1.id
    )
    db.add(subscription1)
    db.commit()

    payment2 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment2)
    db.commit()

    subscription2 = models.Subscription(
        student_id=student_beginner2.id,
        subscription_template_id=subscription_template_group2.id,
        payment_id=payment2.id
    )
    db.add(subscription2)
    db.commit()

    payment3 = models.Payment(
        payment_type_id=payment_type_cash.id
    )
    db.add(payment3)
    db.commit()

    subscription3 = models.Subscription(
        student_id=student_beginner3.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment3.id
    )
    db.add(subscription3)
    db.commit()

    payment4 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment4)
    db.commit()

    subscription4 = models.Subscription(
        student_id=student_beginner4.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment4.id
    )
    db.add(subscription4)
    db.commit()

    payment5 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment5)
    db.commit()

    subscription5 = models.Subscription(
        student_id=student_beginner5.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment5.id
    )
    db.add(subscription5)
    db.commit()

    payment6 = models.Payment(
        payment_type_id=payment_type_cash.id
    )
    db.add(payment6)
    db.commit()

    subscription6 = models.Subscription(
        student_id=student_beginner6.id,
        subscription_template_id=subscription_template_group2.id,
        payment_id=payment6.id
    )
    db.add(subscription6)
    db.commit()

    payment7 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment7)
    db.commit()

    subscription7 = models.Subscription(
        student_id=student_beginner7.id,
        subscription_template_id=subscription_template_group2.id,
        payment_id=payment7.id
    )
    db.add(subscription7)
    db.commit()

    payment8 = models.Payment(
        payment_type_id=payment_type_cash.id
    )
    db.add(payment8)
    db.commit()

    subscription8 = models.Subscription(
        student_id=student_beginner8.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment8.id
    )
    db.add(subscription8)
    db.commit()

    payment9 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment9)
    db.commit()

    subscription9 = models.Subscription(
        student_id=student_beginner9.id,
        subscription_template_id=subscription_template_group1.id,
        payment_id=payment9.id
    )
    db.add(subscription9)
    db.commit()

    payment10 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment10)
    db.commit()

    subscription10 = models.Subscription(
        student_id=student_beginner10.id,
        subscription_template_id=subscription_template_group3.id,
        payment_id=payment10.id
    )
    db.add(subscription10)
    db.commit()

    payment11 = models.Payment(
        payment_type_id=payment_type_card.id
    )
    db.add(payment11)
    db.commit()

    subscription11 = models.Subscription(
        student_id=student_advanced1.id,
        subscription_template_id=subscription_template_indiv.id,
        payment_id=payment11.id
    )
    db.add(subscription11)
    db.commit()

    payment12 = models.Payment(
        payment_type_id=payment_type_cash.id
    )
    db.add(payment12)
    db.commit()

    subscription12 = models.Subscription(
        student_id=student_advanced3.id,
        subscription_template_id=subscription_template_indiv.id,
        payment_id=payment12.id
    )
    db.add(subscription12)
    db.commit()

    classroom1 = models.Classroom(
        name="Зал 101",
        description="Наш любимый зал"
    )
    db.add(classroom1)
    db.commit()

    classroom2 = models.Classroom(
        name="Зал 102"
    )
    db.add(classroom2)
    db.commit()

    classroom3 = models.Classroom(
        name="Зал 201"
    )
    db.add(classroom3)
    db.commit()

    classroom4 = models.Classroom(
        name="Зал 202"
    )
    db.add(classroom4)
    db.commit()

    lesson1 = models.Lesson(
        name="Танго. Введение",
        description="Постигаем азы танго",
        lesson_type_id=lesson_type_tango_group.id,
        start_time=datetime.now(timezone.utc) - timedelta(days=7),
        finish_time=datetime.now(timezone.utc) - timedelta(days=7) + timedelta(minutes=90),
        classroom_id=classroom1.id,
        group_id=group_beginner_tango.id
    )
    db.add(lesson1)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson1.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription2.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription7.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription3.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription8.id,
        lesson_id=lesson1.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson2 = models.Lesson(
        name="Групповое занятие по танго",
        lesson_type_id=lesson_type_tango_group.id,
        start_time=datetime.now(timezone.utc),
        finish_time=datetime.now(timezone.utc) + timedelta(minutes=90),
        classroom_id=classroom2.id,
        group_id=group_beginner_tango.id
    )
    db.add(lesson2)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson2.id
    )
    db.add(teacher_lesson)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson2.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription6.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription2.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription7.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription3.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription8.id,
        lesson_id=lesson2.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson3 = models.Lesson(
        name="Групповое занятие по танго",
        lesson_type_id=lesson_type_tango_group.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=7),
        finish_time=datetime.now(timezone.utc) + timedelta(days=7) + timedelta(minutes=90),
        classroom_id=classroom2.id,
        group_id=group_beginner_tango.id
    )
    db.add(lesson3)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson3.id
    )
    db.add(teacher_lesson)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson3.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription6.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription2.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription7.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription3.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription8.id,
        lesson_id=lesson3.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson4 = models.Lesson(
        name="Групповое занятие по хип-хопу",
        lesson_type_id=lesson_type_hiphop_group.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=2),
        finish_time=datetime.now(timezone.utc) + timedelta(days=2) + timedelta(minutes=90),
        classroom_id=classroom4.id,
        group_id=group_beginner_hiphop.id,
        are_neighbours_allowed=True
    )
    db.add(lesson4)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher3.id,
        lesson_id=lesson4.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription4.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription5.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription9.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription10.id,
        lesson_id=lesson4.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson5 = models.Lesson(
        name="Групповое занятие по хип-хопу",
        lesson_type_id=lesson_type_hiphop_group.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=9),
        finish_time=datetime.now(timezone.utc) + timedelta(days=9) + timedelta(minutes=90),
        classroom_id=classroom4.id,
        group_id=group_beginner_hiphop.id,
        are_neighbours_allowed=True
    )
    db.add(lesson5)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher3.id,
        lesson_id=lesson5.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription1.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription4.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription5.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription9.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription10.id,
        lesson_id=lesson5.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson6 = models.Lesson(
        name="Индивидуальное занятие по танго в паре",
        lesson_type_id=lesson_type_tango_pair.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        finish_time=datetime.now(timezone.utc) + timedelta(days=1) + timedelta(minutes=60),
        classroom_id=classroom3.id,
        group_id=group_advanced_tango.id
    )
    db.add(lesson6)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher1.id,
        lesson_id=lesson6.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription11.id,
        lesson_id=lesson6.id
    )
    db.add(lesson_subscription)
    db.commit()

    lesson7 = models.Lesson(
        name="Индивидуальное занятие по хип-хопу",
        lesson_type_id=lesson_type_hiphop_indiv.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=9) + timedelta(minutes=15),
        finish_time=datetime.now(timezone.utc) + timedelta(days=9) + timedelta(minutes=75),
        classroom_id=classroom4.id,
        group_id=group_advanced_hiphop.id,
        are_neighbours_allowed=True
    )
    db.add(lesson7)
    db.commit()

    teacher_lesson = models.TeacherLesson(
        teacher_id=teacher2.id,
        lesson_id=lesson7.id
    )
    db.add(teacher_lesson)
    db.commit()

    lesson_subscription = models.LessonSubscription(
        subscription_id=subscription12.id,
        lesson_id=lesson7.id
    )
    db.add(lesson_subscription)
    db.commit()

    event_type1 = models.EventType(
        name="Лекция",
        description="Информативная и интересная лекция со свободным посещением"
    )
    db.add(event_type1)
    db.commit()

    event_type2 = models.EventType(
        name="Праздник"
    )
    db.add(event_type2)
    db.commit()

    event1 = models.Event(
        event_type_id=event_type1.id,
        name="Лекция по истории танго",
        description="Безумно захватывающая лекция!",
        start_time=datetime.now(timezone.utc) + timedelta(minutes=100)
    )
    db.add(event1)
    db.commit()

    event2 = models.Event(
        event_type_id=event_type1.id,
        name="Лекция по истории хип-хопа",
        start_time=datetime.now(timezone.utc) + timedelta(days=10)
    )
    db.add(event2)
    db.commit()

    event3 = models.Event(
        event_type_id=event_type2.id,
        name="Юбилей Elcentro",
        start_time=datetime.now(timezone.utc) + timedelta(days=14)
    )
    db.add(event3)
    db.commit()

    slot1 = models.Slot(
        teacher_id=teacher1.id,
        day_of_week=1,
        start_time=time(16, 0),
        end_time=time(17, 0)
    )
    db.add(slot1)
    db.commit()

    slot2 = models.Slot(
        teacher_id=teacher2.id,
        day_of_week=2,
        start_time=time(18, 0),
        end_time=time(19, 0)
    )
    db.add(slot2)
    db.commit()

    slot3 = models.Slot(
        teacher_id=teacher2.id,
        day_of_week=4,
        start_time=time(18, 0),
        end_time=time(19, 0)
    )
    db.add(slot3)
    db.commit()

    return "Тестовые данные созданы успешно"
