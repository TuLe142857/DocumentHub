from email.message import EmailMessage
import smtplib

from celery import shared_task

from app.core import get_settings


@shared_task
def send_email_task(
    to: str,
    subject: str,
    html_content: str | None = None,
    plain_content: str | None = None,
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = get_settings().SMTP_SEND_MAIL_FROM
    msg["To"] = to

    if not html_content and not plain_content:
        raise ValueError("Email must have at least one content")

    if plain_content:
        msg.set_content(plain_content)

    if html_content:
        msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP(
        host=get_settings().SMTP_SERVER, port=get_settings().SMTP_PORT
    ) as server:
        if get_settings().SMTP_USE_TLS:
            server.starttls()
        server.login(
            user=get_settings().SMTP_USER,
            password=get_settings().SMTP_PASSWORD.get_secret_value(),
        )
        server.send_message(msg)
