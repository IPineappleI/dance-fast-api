import smtplib
from email.message import EmailMessage

from app.config import settings

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
