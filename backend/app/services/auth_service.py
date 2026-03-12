from typing import Any

from redis import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.models import User
from app.tasks import send_email_task
from app.utils import generate_otp, render_template

from .jwt_service import JWTService


class AuthService:
    def __init__(
        self, jwt_service: JWTService, redis_client: Redis, db_session: Session
    ):
        self.jwt_service = jwt_service
        self.redis_client = redis_client
        self.db_session = db_session

    def __generate_access_token(
        self, sub: str, claim: dict[str, Any] | None = None, fresh: bool = True
    ) -> str:
        return self.jwt_service.generate_access_token(sub=sub, fresh=fresh, claim=claim)

    def __generate_refresh_token(
        self, sub: str, claim: dict[str, Any] | None = None
    ) -> str:
        return self.jwt_service.generate_refresh_token(sub=sub, claim=claim)

    def request_registration(self, email: str):
        if User.get_by_identity(self.db_session, email) is not None:
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Email already exists"
            )

        otp_code = generate_otp()
        send_email_task.delay(
            to=email,
            subject="Registration request",
            html_content=render_template("mail", {"otp_code": otp_code}),
            plain_content=f"otp_code: {otp_code}",
        )
        self.redis_client.set(f"otp_{email}", otp_code, ex=5 * 60)

    def verify_registration(self, email: str, otp_code: str) -> str:
        otp_key = f"otp_{email}"
        otp_in_cache = self.redis_client.get(otp_key)
        if not otp_in_cache or otp_in_cache.decode() != otp_code:
            raise AppException(ErrorCode.INVALID_CODE)

    def complete_registration(self) -> tuple[str, str]:
        """
        Returns: tuple[str, str]: access_token, refresh_token
        """
        pass

    def login(self, identity: str, password: str) -> tuple[str, str]:
        """

        Returns: tuple[str, str]: access_token, refresh_token

        """
        user = User.get_by_identity(self.db_session, identity)
        if not user or not user.verify_password(password):
            raise AppException(
                ErrorCode.LOGIN_FAILED, "identity or password is invalid"
            )

        return (
            self.__generate_access_token(sub=str(user.id), fresh=True),
            self.__generate_refresh_token(sub=str(user.id)),
        )

    def refresh_access_token(self):
        pass

    def forgot_password(self):
        pass

    def reset_password(self):
        pass
