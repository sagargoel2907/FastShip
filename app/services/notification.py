from fastapi import BackgroundTasks
from fastapi_mail import (
    FastMail,
    ConnectionConfig,
    MessageSchema,
    MessageType,
    NameEmail,
)
from pydantic import EmailStr

from app.config import MAIL_TEMPLATES_FOLDER, notification_settings


class NotificationService:
    def __init__(self, tasks: BackgroundTasks) -> None:
        connection_config = ConnectionConfig(
            **notification_settings.model_dump(), TEMPLATE_FOLDER=MAIL_TEMPLATES_FOLDER
        )
        self._fastmail = FastMail(config=connection_config)
        self._tasks = tasks

    async def send_mail(self, recipients: list[EmailStr], subject: str, body: str):
        self._tasks.add_task(
            self._fastmail.send_message,
            message=MessageSchema(
                recipients=[NameEmail(name="", email=email) for email in recipients],
                subject=subject,
                body=body,
                subtype=MessageType.plain,
            ),
        )

    async def send_email_with_template(
        self,
        recipients: list[EmailStr],
        subject: str,
        context: dict,
        template_name: str,
    ):
        self._tasks.add_task(
            self._fastmail.send_message,
            message=MessageSchema(
                recipients=[NameEmail(name="", email=email) for email in recipients],
                subject=subject,
                subtype=MessageType.html,
                template_body=context,
            ),
            template_name=template_name,
        )
