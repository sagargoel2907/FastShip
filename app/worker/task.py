from celery import Celery
from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)
from pydantic import EmailStr
from app.config import MAIL_TEMPLATES_FOLDER, notification_settings
from asgiref.sync import async_to_sync


from app.config import db_settings

app = Celery(broker=db_settings.REDIS_URL(2), backend=db_settings.REDIS_URL(2))


connection_config = ConnectionConfig(
**notification_settings.model_dump(), TEMPLATE_FOLDER=MAIL_TEMPLATES_FOLDER
)

fastmail = FastMail(config=connection_config)

send_message = async_to_sync(fastmail.send_message)

@app.task
def send_email(recipients: list[EmailStr], subject: str, body: str):
    print(__name__, 'inside the function')
    send_message(
        MessageSchema(
            recipients=[NameEmail(name="", email=email) for email in recipients],
            subject=subject,
            body=body,
            subtype=MessageType.plain,
        )
    )
    return "email sent"


@app.task
def send_email_with_template(
    recipients: list[EmailStr], subject: str, template_name: str, context: dict
):
    send_message(
        MessageSchema(
            recipients=[NameEmail(name="", email=email) for email in recipients],
            subject=subject,
            template_body=context,
            subtype=MessageType.html,
        ),
        template_name=template_name,
    )
    return "email sent"
