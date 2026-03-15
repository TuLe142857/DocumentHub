from typing import Annotated, Any

from fastapi import Depends
from redis import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.dependencies import DBSessionDep, RedisDep
from app.models import *
from app.tasks import send_email_task
from app.utils import generate_otp, render_template

from .jwt_service import JWTService, JWTServiceDep
from .mail_service import MailService, MailServiceDep


class AuthService:
    def __init__(
        self,
        jwt_service: JWTService,
        redis_client: Redis,
        db_session: Session,
        mail_service: MailService,
    ):
        self.jwt_service = jwt_service
        self.redis_client = redis_client
        self.db_session = db_session
        self.mail_service = mail_service

    def __generate_access_token(self, user: User, fresh: bool = True) -> str:
        additional_claim = None
        return self.jwt_service.generate_access_token(
            sub=str(user.id), fresh=fresh, claim=additional_claim
        )

    def __generate_refresh_token(self, user: User) -> str:
        additional_claim = None
        return self.jwt_service.generate_refresh_token(
            sub=str(user.id), claim=additional_claim
        )

    def get_user_id(
        self,
        token_payload: dict[str, Any],
        required_active: bool = False,
        require_role: str | None = None,
    ) -> int:
        """
        get user id from jwt token payload
        Args:
            require_role: check user role match role name
            required_active: check user is active
            token_payload: access/refresh token payload as dict[str, Any]

        Returns: user id
        """
        if not token_payload.get("sub"):
            raise AppException(
                ErrorCode.INVALID_JWT_TOKEN,
                "JWT token is invalid.(Require 'sub' in token payload)",
            )
        user_id = int(token_payload["sub"])

        if (not required_active) or (require_role is None):
            return user_id

        user: User = self.db_session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if user is None:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")

        if required_active and not user.is_active:
            raise AppException(ErrorCode.USER_IS_IN_ACTIVE)

        if (require_role is not None) and (
            require_role.strip().lower() != user.role.name.lower()
        ):
            raise AppException(ErrorCode.FORBIDDEN, "Role mismatch")
        return user_id

    def request_registration(self, email: str):
        if User.get_by_identity(email, self.db_session) is not None:
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Email already exists"
            )

        otp_code = generate_otp()
        # send_email_task.delay(
        #     to=email,
        #     subject="Registration request",
        #     html_content=render_template("mail", {"otp_code": otp_code}),
        #     plain_content=f"otp_code: {otp_code}",
        # )
        self.mail_service.send_registration_otp_email(
            to=email, otp_code=otp_code, otp_expire_minutes=5
        )
        self.redis_client.set(f"verify_regis_{email}", otp_code, ex=5 * 60)

    def verify_registration(self, email: str, otp_code: str) -> str:
        otp_key = f"verify_regis_{email}"
        otp_in_cache = self.redis_client.get(otp_key)
        if not otp_in_cache or otp_in_cache.decode() != otp_code:
            raise AppException(ErrorCode.INVALID_CODE, "Invalid OTP")

        self.redis_client.delete(otp_key)

        registration_code = generate_otp()
        registration_key = f"registration_{email}"
        self.redis_client.set(registration_key, registration_code, ex=15 * 60)
        return registration_code

    def complete_registration(
        self, email: str, registration_code: str, username: str, password: str
    ) -> tuple[str, str]:
        """
        Returns: tuple[str, str]: access_token, refresh_token
        """

        # validate registration code
        registration_key = f"registration_{email}"
        registration_code_in_cache = self.redis_client.get(registration_key)
        if (
            not registration_code_in_cache
            or registration_code_in_cache.decode() != registration_code
        ):
            raise AppException(ErrorCode.INVALID_CODE, "Invalid registration code")

        # check email & username already exist
        if (
            User.get_by_identity(username, self.db_session) is not None
            or User.get_by_identity(email, self.db_session) is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Username or Email already exists"
            )

        # add new user
        try:
            role_user = Role.get_or_create("USER", self.db_session)
            new_user = User(
                email=email,
                username=username,
                role=role_user,
                profile=UserProfile(),
            )
            new_user.set_password(password)
            self.db_session.add(new_user)
            self.db_session.commit()
        except IntegrityError:
            raise AppException(ErrorCode.DATA_INTEGRITY_ERROR)

        # create user success, delete registration code
        self.redis_client.delete(registration_key)

        # return access/refresh token
        return (
            self.__generate_access_token(new_user, fresh=True),
            self.__generate_refresh_token(new_user),
        )

    def login(self, identity: str, password: str) -> tuple[str, str]:
        """

        Returns: tuple[str, str]: access_token, refresh_token

        """
        user = User.get_by_identity(identity, self.db_session)
        if not user or not user.verify_password(password):
            raise AppException(
                ErrorCode.LOGIN_FAILED, "identity or password is invalid"
            )

        return (
            self.__generate_access_token(user, fresh=True),
            self.__generate_refresh_token(user),
        )

    def refresh_access_token(self, refresh_token: dict[str, Any] | str) -> str:
        """
        If `refresh_token` is instance of `str`, this method will decode & validate it to payload.
        If `refresh_token` is instance of `dict[str, Any]`, this method with read it as refresh_token_payload.
        Args:
            refresh_token (dict[str, Any] | str): refresh_token(str) or refresh_token_payload(dict[str, Any])

        Returns: new access token

        """
        if isinstance(refresh_token, dict):
            user_id = int(refresh_token.get("sub"))
        else:
            refresh_token_payload = self.jwt_service.validate_refresh_token(
                refresh_token
            )
            user_id = int(refresh_token_payload.get("sub"))
        user = self.db_session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if not user:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User ID not found")
        return self.__generate_access_token(user, fresh=False)

    def forgot_password(self, identity: str):
        user = User.get_by_identity(identity, self.db_session)
        if not user:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")
        self.redis_client.set(
            f"forgot_password_{user.email}", generate_otp(), ex=5 * 60
        )

    def reset_password(self, identity: str, otp_code: str, new_password: str):
        user = User.get_by_identity(identity, self.db_session)
        if not user:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")
        otp_key = f"forgot_password_{user.email}"
        otp_in_cache = self.redis_client.get(otp_key)
        if not otp_in_cache or otp_in_cache.decode() != otp_code:
            raise AppException(ErrorCode.INVALID_CODE, "Invalid OTP")
        user.set_password(new_password)
        self.db_session.commit()
        self.redis_client.delete(otp_key)


def get_auth_service(
    jwt_service: JWTServiceDep,
    redis_client: RedisDep,
    db_session: DBSessionDep,
    mail_service: MailServiceDep,
) -> AuthService:
    return AuthService(jwt_service, redis_client, db_session, mail_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
