import smtplib
from datetime import timedelta
from email.message import EmailMessage

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.auth.jwt import create_token
from app.config import settings
from app.models import User, TeacherGroup, StudentGroup, Teacher, Student

SENDER_EMAIL = settings.SENDER_EMAIL
SENDER_PASSWORD = settings.SENDER_PASSWORD
SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SSL_CONTEXT = settings.SSL_CONTEXT
EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES = settings.EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES


async def send_email(message: EmailMessage):
    message['From'] = SENDER_EMAIL

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)


async def send_email_confirmation_token(user_id, email, name):
    expires_delta = timedelta(minutes=EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES)

    email_confirmation_token = create_token(
        data={'user_id': str(user_id)},
        expires_delta=expires_delta
    )

    message = EmailMessage()
    message['To'] = email
    message['Subject'] = f'Школа танцев. Подтверждение адреса электронной почты'
    message.set_content(f'Здравствуйте, {name}!\n\n'
                        f'Пожалуйста, подтвердите адрес электронной почты, перейдя по следующей ссылке:\n'
                        f'http://localhost:8000/auth/confirm-email/{email_confirmation_token}')

    await send_email(message)


async def send_new_event_email(event, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student)
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. {event.name}'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Рады сообщить вам о новом предстоящем мероприятии: {event.name}\n'
            f'Мероприятие начнётся {event.start_time.date()} в {event.start_time.time()} по Москве'
        )
        content += f'\nОписание мероприятия:\n{event.description}' if event.description else ''
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_event_rescheduled_email(event, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student)
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. {event.name}'
        message.set_content(f'Здравствуйте, {user.first_name}!\n\n'
                            f'Уведомляем вас о том, что мероприятие "{event.name}" было перенесено\n'
                            f'Мероприятие начнётся {event.start_time.date()} в {event.start_time.time()} по Москве')
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_event_cancelled_email(event, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student)
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. {event.name}'
        message.set_content(f'Здравствуйте, {user.first_name}!\n\n'
                            f'С сожалением сообщаем вам, что мероприятие "{event.name}" было отменено')
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_teacher_email(teacher, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student),
        User.id != teacher.user.id
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Новый преподаватель!'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Рады сообщить вам, что у нас появился новый преподаватель: '
            f'{teacher.user.last_name} {teacher.user.first_name}'
        )
        content += f' {teacher.user.middle_name}' if teacher.user.middle_name else ''
        content += (
            f'\nВот что преподаватель пишет о себе:\n{teacher.user.description}'
        ) if teacher.user.description else ''
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_teacher_terminated_email(teacher, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student)
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Изменение преподавательского состава'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'С сожалением сообщаем, что {teacher.user.last_name} {teacher.user.first_name}'
        )
        content += f' {teacher.user.middle_name}' if teacher.user.middle_name else ''
        content += f' больше не преподаёт в нашей школе'
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_classroom_email(classroom, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student)
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Новый зал!'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Рады сообщить вам, что у нас появился новый зал: {classroom.name}'
        )
        content += (
            f'\nОписание зала:\n{classroom.description}'
        ) if classroom.description else ''
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_classroom_terminated_email(classroom, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(User.teacher, User.student)
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. {classroom.name}'
        message.set_content(f'Здравствуйте, {user.first_name}!\n\n'
                            f'Сообщаем вам о том, что зал "{classroom.name}" не доступен для занятий')
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_group_lesson_email(lesson, db: Session):
    group_teacher_ids = [teacher.id for teacher in lesson.group.teachers]
    group_student_ids = [student.id for student in lesson.group.students]
    users = db.query(User).join(Teacher, isouter=True).join(Student, isouter=True).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(
            and_(
                Teacher.id != None,
                Teacher.id.in_(group_teacher_ids)
            ),
            and_(
                Student.id != None,
                Student.id.in_(group_student_ids)
            )
        )
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. {lesson.group.name}'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'В расписании появилось новое занятие группы "{lesson.group.name}"\n'
            f'Занятие начнётся {lesson.start_time.date()} в {lesson.start_time.time()} по Москве\n'
            f'Название занятия: {lesson.name}'
        )
        content += f'\nОписание занятия:\n{lesson.description}' if lesson.description else ''
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


def get_lesson_users(lesson, db: Session):
    lesson_teacher_ids = [teacher.id for teacher in lesson.actual_teachers]
    lesson_student_ids = [student.id for student in lesson.actual_students]
    users = db.query(User).join(Teacher, isouter=True).join(Student, isouter=True).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        or_(
            and_(
                Teacher.id != None,
                Teacher.id.in_(lesson_teacher_ids)
            ),
            and_(
                Student.id != None,
                Student.id.in_(lesson_student_ids)
            )
        )
    ).all()
    return users


async def send_lesson_rescheduled_email(lesson, db: Session):
    users = get_lesson_users(lesson, db)
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Перенос занятия'
        message.set_content(f'Здравствуйте, {user.first_name}!\n\n'
                            f'Уведомляем вас о том, что занятие "{lesson.name}" было перенесено\n'
                            f'Занятие начнётся {lesson.start_time.date()} в {lesson.start_time.time()} по Москве')
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_lesson_cancelled_email(lesson, db: Session):
    users = get_lesson_users(lesson, db)
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Отмена занятия'
        message.set_content(f'Здравствуйте, {user.first_name}!\n\n'
                            f'С сожалением сообщаем вам, что занятие "{lesson.name}" было отменено')
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_group_email(group, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        User.student
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Новая группа!'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Рады сообщить вам, что у нас появилась новая группа: {group.name}'
        )
        content += (
            f'\nОписание группы:\n{group.description}'
        ) if group.description else ''
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_subscription_template_email(subscription_template, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        User.student
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Новый шаблон абонемента!'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Рады сообщить вам, что у нас появился новый шаблон абонемента: {subscription_template.name}'
        )
        content += (
            f'\nОписание шаблона:\n{subscription_template.description}'
        ) if subscription_template.description else ''
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_payment_type_email(payment_type, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        User.student
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Новый способ оплаты!'
        content = (
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Рады сообщить вам, что у нас появился новый способ оплаты: {payment_type.name}'
        )
        message.set_content(content)
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_payment_type_terminated_email(payment_type, db: Session):
    users = db.query(User).where(
        User.terminated == False,
        User.email_confirmed == True,
        User.receive_email == True,
        User.student
    ).all()
    for user in users:
        message = EmailMessage()
        message['To'] = user.email
        message['Subject'] = f'Школа танцев. Способ оплаты "{payment_type.name}"'
        message.set_content(f'Здравствуйте, {user.first_name}!\n\n'
                            f'Сообщаем вам о том, что способ оплаты "{payment_type.name}" не доступен')
        try:
            await send_email(message)
        except Exception as e:
            print(e)


async def send_new_payment_email(payment, user):
    message = EmailMessage()
    message['To'] = user.email
    message['Subject'] = f'Школа танцев. Оплата произведена'
    content = (
        f'Здравствуйте, {user.first_name}!\n\n'
        f'Оплата произведена успешно!'
    )
    content += (
        f'\nДетали операции:\n{payment.details}'
    ) if payment.details else ''
    message.set_content(content)
    try:
        await send_email(message)
    except Exception as e:
        print(e)


async def send_payment_terminated_email(payment, user):
    message = EmailMessage()
    message['To'] = user.email
    message['Subject'] = f'Школа танцев. Оплата отменена'
    content = (
        f'Здравствуйте, {user.first_name}!\n\n'
        f'Оплата была отменена'
    )
    content += (
        f'\nДетали операции:\n{payment.details}'
    ) if payment.details else ''
    message.set_content(content)
    try:
        await send_email(message)
    except Exception as e:
        print(e)


async def send_new_individual_lesson_email(lesson):
    student_user = lesson.actual_students[0].user
    teacher_user = lesson.actual_teachers[0].user
    message = EmailMessage()
    message['To'] = student_user.email
    message['Subject'] = f'Школа танцев. {lesson.name}'
    content = (
        f'Здравствуйте, {student_user.first_name}!\n\n'
        f'Преподаватель {teacher_user.last_name} {teacher_user.first_name}'
    )
    content += f' {teacher_user.middle_name}' if teacher_user.middle_name else ''
    content += (
        f' запланировал индивидуальное занятие с вашим участием\n'
        f'Занятие начнётся {lesson.start_time.date()} в {lesson.start_time.time()} по Москве'
    )
    content += (
        f'\nОписание занятия:\n{lesson.description}'
    ) if lesson.description else ''
    message.set_content(content)
    try:
        await send_email(message)
    except Exception as e:
        print(e)


async def send_new_lesson_request_email(lesson_request):
    student_user = lesson_request.actual_students[0].user
    teacher_user = lesson_request.actual_teachers[0].user
    message = EmailMessage()
    message['To'] = teacher_user.email
    message['Subject'] = f'Школа танцев. Новая заявка на индивидуальное занятие'
    content = (
        f'Здравствуйте, {teacher_user.first_name}!\n\n'
        f'Ученик {student_user.last_name} {student_user.first_name}'
    )
    content += f' {student_user.middle_name}' if student_user.middle_name else ''
    content += (
        f' отправил вам заявку на индивидуальное занятие'
        f' {lesson_request.start_time.date()} в {lesson_request.start_time.time()} по Москве'
    )
    content += (
        f'\nОписание заявки:\n{lesson_request.description}'
    ) if lesson_request.description else ''
    message.set_content(content)
    try:
        await send_email(message)
    except Exception as e:
        print(e)


async def send_lesson_request_accepted_email(lesson):
    student_user = lesson.actual_students[0].user
    teacher_user = lesson.actual_teachers[0].user
    message = EmailMessage()
    message['To'] = student_user.email
    message['Subject'] = f'Школа танцев. Заявка на индивидуальное занятие принята'
    content = (
        f'Здравствуйте, {student_user.first_name}!\n\n'
        f'Преподаватель {teacher_user.last_name} {teacher_user.first_name}'
    )
    content += f' {teacher_user.middle_name}' if teacher_user.middle_name else ''
    content += f' принял вашу заявку на индивидуальное занятие'
    message.set_content(content)
    try:
        await send_email(message)
    except Exception as e:
        print(e)


async def send_lesson_request_declined_email(lesson):
    student_user = lesson.actual_students[0].user
    teacher_user = lesson.actual_teachers[0].user
    message = EmailMessage()
    message['To'] = student_user.email
    message['Subject'] = f'Школа танцев. Заявка на индивидуальное занятие отклонена'
    content = (
        f'Здравствуйте, {student_user.first_name}!\n\n'
        f'Преподаватель {teacher_user.last_name} {teacher_user.first_name}'
    )
    content += f' {teacher_user.middle_name}' if teacher_user.middle_name else ''
    content += f' отклонил вашу заявку на индивидуальное занятие'
    message.set_content(content)
    try:
        await send_email(message)
    except Exception as e:
        print(e)
