from typing import Annotated

from fastapi import Depends

from app.tasks import send_email_task
from app.utils import render_template


class MailService:
    def __init__(self):
        pass

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str | None = None,
        plain_content: str | None = None,
    ):
        """
        Send an email in background(use celery task).
        Args:
            to: receiver email
            subject: mail subject
            html_content: html content
            plain_content: plain content

        Returns:

        """
        send_email_task.delay(
            to=to,
            subject=subject,
            html_content=html_content,
            plain_content=plain_content,
        )

    def send_registration_otp_email(
        self, to: str, otp_code: str, otp_expire_minutes: int
    ):
        html_content = render_template(
            "mail", {"otp_code": otp_code, "expire_minutes": otp_expire_minutes}
        )
        plain_content = f"Registration verify, otp_code: {otp_code}, expire_minutes: {otp_expire_minutes}"
        self.send_email(
            to=to,
            subject="Registration request",
            html_content=html_content,
            plain_content=plain_content,
        )

    def send_registration_complete_email(self, to: str):
        pass

    def send_forgot_password_otp_email(
        self, to: str, otp_code: str, otp_expire_minutes: int
    ):
        pass

    def send_reset_password_complete_email(self, to: str):
        pass


def get_mail_service() -> MailService:
    return MailService()


MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
