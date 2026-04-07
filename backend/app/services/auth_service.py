from typing import Annotated, Literal, Sequence

from fastapi import Depends
from redis import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.core.sercurity import (
    AccessPayloadProvider,
    JWTPayload,
    JWTService,
    JWTServiceDep,
)
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep, RedisDep
from app.models import *
from app.utils import generate_otp

from .mail_service import MailService, MailServiceDep


class AuthService:
    def __init__(
        self,
        crud_user: CRUDUser,
        jwt_service: JWTService,
        redis_client: Redis,
        db_session: Session,
        mail_service: MailService,
    ):
        self.crud_user = crud_user
        self.jwt_service = jwt_service
        self.redis_client = redis_client
        self.db_session = db_session
        self.mail_service = mail_service

    def __generate_access_token(self, user: User, fresh: bool = True) -> str:
        additional_claim = None
        return self.jwt_service.generate_access_token(
            sub=str(user.id), fresh=fresh, claim=additional_claim
        )[0]

    def __generate_refresh_token(self, user: User) -> str:
        additional_claim = None
        return self.jwt_service.generate_refresh_token(
            sub=str(user.id), claim=additional_claim
        )[0]

    def get_user_from_jwt_payload(self, payload: JWTPayload) -> User:
        """
        Raises:
            AppException(ErrorCode.INVALID_CREDENTIALS) when user not found
        """
        return self.crud_user.get(
            int(payload.sub),
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )

    def request_registration(self, email: str):
        if self.crud_user.get_by_identity(email) is not None:
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Email already exists"
            )

        otp_code = generate_otp()
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

        self.mail_service.send_registration_complete_email(to=new_user.email)

        # return access/refresh token
        return (
            self.__generate_access_token(new_user, fresh=True),
            self.__generate_refresh_token(new_user),
        )

    def login(self, identity: str, password: str) -> tuple[str, str]:
        """

        Returns: tuple[str, str]: access_token, refresh_token

        """
        user = self.crud_user.get_by_identity(identity)
        if not user or not user.verify_password(password):
            raise AppException(
                ErrorCode.LOGIN_FAILED, "identity or password is invalid"
            )

        return (
            self.__generate_access_token(user, fresh=True),
            self.__generate_refresh_token(user),
        )

    def refresh_access_token(self, user_id: int) -> str:
        user = self.crud_user.get(user_id)
        if not user:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User ID not found")
        return self.__generate_access_token(user, fresh=False)

    def forgot_password(self, identity: str):
        user = self.crud_user.get_by_identity(identity)
        if not user:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")

        otp_key = f"forgot_password_{user.email}"
        otp_code = generate_otp()
        self.redis_client.set(otp_key, otp_code, ex=5 * 60)
        self.mail_service.send_forgot_password_otp_email(
            to=user.email, otp_code=otp_code, otp_expire_minutes=5
        )

    def reset_password(self, identity: str, otp_code: str, new_password: str):
        user = self.crud_user.get_by_identity(identity)
        if not user:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")

        otp_key = f"forgot_password_{user.email}"
        otp_in_cache = self.redis_client.get(otp_key)
        if not otp_in_cache or otp_in_cache.decode() != otp_code:
            raise AppException(ErrorCode.INVALID_CODE, "Invalid OTP")

        user.set_password(new_password)
        self.db_session.commit()

        self.redis_client.delete(otp_key)
        self.mail_service.send_reset_password_complete_email(to=user.email)


def get_auth_service(
    crud_user: CRUDUserDep,
    jwt_service: JWTServiceDep,
    redis_client: RedisDep,
    db_session: DBSessionDep,
    mail_service: MailServiceDep,
) -> AuthService:
    return AuthService(crud_user, jwt_service, redis_client, db_session, mail_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


class CurrentUserProvider:
    def __init__(self, role: str | Sequence[str] | None = None, optional: bool = False):
        """
        FastAPI dependency that provides the current authenticated user.
        - Validates access token and returns the corresponding active user.
        - Optionally enforces role-based access control.
        Args:
            role:
                Required role(s). Accepts a string or a sequence of strings.
                If None (default), any authenticated user is allowed.
            optional:
                If False (default), raises an exception when the user is not authenticated.
                If True, returns None instead of raising when no user is logged in.
        """
        if role is None:
            self.accept_roles = None
        elif isinstance(role, str):
            self.accept_roles = [role]
        elif isinstance(role, Sequence):
            self.accept_roles = role
        else:
            raise ValueError(
                f"Invalid role type. Expect 'str|Sequence[str]|None', got {type(role)}"
            )
        self.optional = optional

    def __call__(
        self,
        access_payload: Annotated[
            JWTPayload | None, Depends(AccessPayloadProvider(optional=True))
        ],
        auth_service: AuthServiceDep,
    ) -> User | None:
        user = (
            auth_service.get_user_from_jwt_payload(access_payload)
            if (access_payload is not None)
            else None
        )
        if user is None:
            if self.optional:
                return None
            else:
                raise AppException(ErrorCode.UNAUTHORIZED, "Required login")
        else:
            # check active
            if not user.is_active:
                raise AppException(ErrorCode.USER_INACTIVE, "User inactive")

            # check role
            if (self.accept_roles is not None) and not (
                user.role.name in self.accept_roles
            ):
                raise AppException(
                    ErrorCode.FORBIDDEN,
                    f"User role not allowed. Current use role: {user.role.name}, allowed roles: {self.accept_roles}",
                )
            return user


CurrentUserDep = Annotated[User, Depends(CurrentUserProvider(role=["USER", "ADMIN"]))]
OptionalCurrentUserDep = Annotated[
    User | None, Depends(CurrentUserProvider(role=["USER", "ADMIN"], optional=True))
]
CurrentAdminDep = Annotated[User, Depends(CurrentUserProvider(role=["ADMIN"]))]
