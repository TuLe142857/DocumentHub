import dataclasses
import datetime
from typing import Annotated, Any, ClassVar, Literal
import uuid

from fastapi import Body, Depends
from fastapi.security import APIKeyCookie, APIKeyHeader
import jwt

from app.core import AppException, ErrorCode, get_settings


@dataclasses.dataclass(frozen=True)
class JWTPayload:
    # Static Constant
    RESERVED_KEYS: ClassVar[list[str]] = ["jti", "sub", "token_type", "fresh", "exp"]

    # Fields
    sub: str
    token_type: Literal["access", "refresh"]
    fresh: bool
    exp: int
    claim: dict[str, Any] = dataclasses.field(default_factory=dict)
    jti: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """
        Handle validate
        """
        if self.token_type not in ["access", "refresh"]:
            raise ValueError(
                f"Invalid token_type '{self.token_type}'. Available token_type values are ['access', 'refresh']"
            )
        for extra_key in self.claim:
            if extra_key in JWTPayload.RESERVED_KEYS:
                raise ValueError(
                    f"Keyword '{extra_key}' is reserved and cannot be overridden in claim."
                )

    def to_dict(self) -> dict[str, Any]:
        data = {k: v for k, v in self.claim.items()}
        for k in JWTPayload.RESERVED_KEYS:
            data[k] = getattr(self, k)
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "JWTPayload":
        """
        Raises: ValueError when validate failed
        """
        for required_key in JWTPayload.RESERVED_KEYS:
            if required_key not in data:
                raise ValueError(
                    f"Missing required key '{required_key}' when creating JWTPayload from dict."
                )

        init_fields = {k: data[k] for k in JWTPayload.RESERVED_KEYS}
        claim = {k: data[k] for k in data if k not in JWTPayload.RESERVED_KEYS}
        return JWTPayload(**init_fields, claim=claim)


class JWTService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_seconds: int = 5 * 60,
        refresh_token_expire_seconds: int = 7 * 24 * 60 * 60,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_seconds = access_token_expire_seconds
        self.refresh_token_expire_seconds = refresh_token_expire_seconds

    def generate_token(self, payload: JWTPayload) -> str:
        return jwt.encode(payload.to_dict(), self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str) -> JWTPayload:
        try:
            payload_dict = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            payload = JWTPayload.from_dict(payload_dict)
            return payload
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCode.JWT_TOKEN_EXPIRED, "JWT token has expired")
        except jwt.InvalidTokenError:
            raise AppException(ErrorCode.INVALID_JWT_TOKEN, "Invalid JWT token")
        except ValueError:
            # when validate jwt payload
            raise AppException(ErrorCode.INVALID_JWT_TOKEN, "Invalid JWT token")

    def generate_access_token(
        self, sub: str, fresh: bool = False, claim: dict | None = None
    ) -> tuple[str, JWTPayload]:
        exp_datetime = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(seconds=int(self.access_token_expire_seconds))
        exp_int = int(exp_datetime.timestamp())
        payload = JWTPayload(
            sub=sub,
            token_type="access",
            fresh=fresh,
            exp=exp_int,
            claim=claim if (claim is not None) else {},
        )
        return self.generate_token(payload), payload

    def generate_refresh_token(
        self, sub: str, claim: dict | None = None
    ) -> tuple[str, JWTPayload]:
        exp_datetime = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(seconds=int(self.refresh_token_expire_seconds))
        exp_int = int(exp_datetime.timestamp())
        payload = JWTPayload(
            sub=sub,
            token_type="refresh",
            fresh=True,
            exp=exp_int,
            claim=claim if (claim is not None) else {},
        )
        return self.generate_token(payload), payload

    def validate_refresh_token(self, refresh_token: str) -> JWTPayload:
        payload = self.validate_token(refresh_token)
        if payload.token_type != "refresh":
            raise AppException(
                ErrorCode.INVALID_JWT_TOKEN,
                f"Require JWT token type 'refresh' got '{payload.token_type}' instead.",
            )
        return payload

    def validate_access_token(
        self, access_token: str, require_fresh: bool = False
    ) -> JWTPayload:
        payload = self.validate_token(access_token)
        if payload.token_type != "access":
            raise AppException(
                ErrorCode.INVALID_JWT_TOKEN,
                f"Require JWT token type 'access' got '{payload.token_type}' instead.",
            )
        if require_fresh and (not payload.fresh):
            raise AppException(
                ErrorCode.JWT_TOKEN_NOT_FRESH, f"Require fresh JWT access token"
            )
        return payload


def get_jwt_service() -> JWTService:
    settings = get_settings()
    return JWTService(
        secret_key=settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_seconds=settings.JWT_ACCESS_TOKEN_EXPIRES,
        refresh_token_expire_seconds=settings.JWT_REFRESH_TOKEN_EXPIRES,
    )


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]

AccessCookieDep = Annotated[
    str | None,
    Depends(
        APIKeyCookie(
            name=get_settings().JWT_ACCESS_COOKIE_NAME,
            auto_error=False,
            scheme_name="AccessTokenCookie",
        )
    ),
]
AccessHeaderDep = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name="Authorization", auto_error=False, scheme_name="AccessTokenHeader"
        )
    ),
]


class AccessPayloadProvider:
    """
    A callable class for fastapi dependencies.
    Use to decode, validate and provide JWT access payload stored on cookie or header.
    """

    def __init__(self, optional: bool = False, fresh: bool = False):
        self.optional = optional
        self.fresh = fresh

    def __call__(
        self,
        jwt_service: JWTServiceDep,
        access_cookie: AccessCookieDep = None,
        access_header: AccessHeaderDep = None,
    ) -> JWTPayload | None:
        if access_header is not None:
            if not access_header.startswith("Bearer"):
                raise AppException(
                    ErrorCode.INVALID_JWT_TOKEN,
                    "Invalid JWT token format on header. Token provided by header must start with 'Bearer'",
                )
            parts = access_header.split()
            if len(parts) == 2:
                access_token = parts[1]
            else:
                raise AppException(
                    ErrorCode.INVALID_JWT_TOKEN, "Invalid Token format on header."
                )

        else:
            access_token = access_cookie

        if access_token is None:
            if self.optional:
                return None
            else:
                raise AppException(ErrorCode.UNAUTHORIZED, "Require JWT Access Token")
        else:
            return jwt_service.validate_access_token(
                access_token=access_token, require_fresh=self.fresh
            )


RefreshCookieDep = Annotated[
    str | None,
    Depends(
        APIKeyCookie(
            name=get_settings().JWT_REFRESH_COOKIE_NAME,
            auto_error=False,
            scheme_name="RefreshTokenCookie",
        )
    ),
]
RefreshBodyDep = Annotated[str | None, Body(alias="refresh_token", embed=True)]


class RefreshPayloadProvider:
    """
    A callable class for fastapi dependencies.
    Use to decode, validate and provide JWT refresh payload stored on cookie or header.
    """

    def __init__(self, optional: bool = False):
        self.optional = optional

    def __call__(
        self,
        jwt_service: JWTServiceDep,
        refresh_cookie: RefreshCookieDep = None,
        refresh_body: RefreshBodyDep = None,
    ) -> JWTPayload | None:

        refresh_token = refresh_body if (refresh_body is not None) else refresh_cookie

        if refresh_token is None:
            if self.optional:
                return None
            else:
                raise AppException(ErrorCode.UNAUTHORIZED, "Require JWT refresh token")
        else:
            return jwt_service.validate_refresh_token(refresh_token)


AccessToken = Annotated[JWTPayload, Depends(AccessPayloadProvider())]

FreshAccessToken = Annotated[JWTPayload, Depends(AccessPayloadProvider(fresh=True))]

OptionalAccessToken = Annotated[
    JWTPayload | None, Depends(AccessPayloadProvider(optional=True))
]

RefreshToken = Annotated[JWTPayload, Depends(RefreshPayloadProvider())]
