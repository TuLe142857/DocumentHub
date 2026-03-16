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
            "registration_otp_mail",
            {"otp_code": otp_code, "expire_minutes": otp_expire_minutes},
        )
        plain_content = f"Registration verify, otp_code: {otp_code}, this otp will expire in {otp_expire_minutes} minutes"
        self.send_email(
            to=to,
            subject="Registration request",
            html_content=html_content,
            plain_content=plain_content,
        )

    def send_registration_complete_email(self, to: str):
        html_content = render_template("registration_complete_mail")
        plain_content = "registration complete"
        self.send_email(
            to=to,
            subject="Registration complete",
            html_content=html_content,
            plain_content=plain_content,
        )

    def send_forgot_password_otp_email(
        self, to: str, otp_code: str, otp_expire_minutes: int
    ):
        html_content = render_template(
            "reset_password_otp_mail",
            {"otp_code": otp_code, "expire_minutes": otp_expire_minutes},
        )
        plain_content = f"Password reset otp\nopt code: {otp_code}, this otp will expire in {otp_expire_minutes} minutes"
        self.send_email(
            to=to,
            subject="Password reset",
            html_content=html_content,
            plain_content=plain_content,
        )

    def send_reset_password_complete_email(self, to: str):
        html_content = render_template("reset_password_success_mail")
        plain_content = "Your password is reset successfully!"
        self.send_email(
            to=to,
            subject="Password reset successfully",
            html_content=html_content,
            plain_content=plain_content,
        )


def get_mail_service() -> MailService:
    return MailService()


MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
