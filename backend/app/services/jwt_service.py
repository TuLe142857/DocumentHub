from dataclasses import dataclass
import datetime
from typing import Annotated, Any, Literal

from fastapi import Depends, Request
import jwt

from app.core import AppException, ErrorCode, get_settings


@dataclass(frozen=True)
class JWTPayload:
    sub: str
    token_type: Literal["access", "refresh"]
    fresh: bool
    exp: int
    claim: dict[str, Any]

    def __dict__(self) -> dict[str, Any]:
        data = {k: v for k, v in self.claim.items()}
        data["sub"] = self.sub
        data["type"] = self.token_type
        data["fresh"] = self.fresh
        data["exp"] = self.exp
        return data


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

    def generate_access_token(
        self, sub: str, fresh: bool = False, claim: dict | None = None
    ):
        payload = {
            "sub": sub,
            "type": "access",
            "fresh": fresh,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=int(self.access_token_expire_seconds)),
        }
        if claim:
            for key, value in claim.items():
                payload[key] = value
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, sub: str, claim: dict | None = None):
        payload = {
            "sub": sub,
            "type": "refresh",
            "fresh": True,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=int(self.refresh_token_expire_seconds)),
        }
        if claim:
            for key, value in claim.items():
                payload[key] = value
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str) -> JWTPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            token_type = payload.get("type")
            sub = payload.get("sub")
            fresh = payload.get("fresh")
            exp = payload.get("exp")
            claim = {
                k: v
                for k, v in payload.items()
                if (k not in ["sub", "type", "fresh", "exp"])
            }

            if token_type != "access" and token_type != "refresh":
                raise AppException(
                    ErrorCode.INVALID_JWT_TOKEN,
                    f"Invalid JWT token type. Expect 'access' or 'refresh' but got {token_type} instead.",
                )
            return JWTPayload(
                sub=sub, token_type=token_type, fresh=fresh, exp=exp, claim=claim
            )
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCode.JWT_TOKEN_EXPIRED, "JWT token has expired")
        except jwt.InvalidTokenError:
            raise AppException(ErrorCode.INVALID_JWT_TOKEN, "Invalid JWT token")

    def validate_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Raises AppException if the refresh token is invalid
        :param refresh_token: refresh token
        :return: payload as dict
        """
        try:
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )
            if payload.get("type") != "refresh":
                raise AppException(
                    ErrorCode.INVALID_JWT_TOKEN, "Token is not type refresh"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCode.JWT_TOKEN_EXPIRED, "Refresh token has expired")
        except jwt.InvalidTokenError:
            raise AppException(
                ErrorCode.INVALID_JWT_TOKEN, "Invalid token refresh token"
            )

    def validate_access_token(
        self, access_token: str, require_fresh: bool = False
    ) -> dict[str, Any]:
        """
        Raises AppException if the access token is invalid
        :param access_token: access token
        :param require_fresh: require fresh token
        :return: payload as dict
        """
        try:
            payload = jwt.decode(
                access_token, self.secret_key, algorithms=[self.algorithm]
            )
            if payload.get("type") != "access":
                raise AppException(
                    ErrorCode.INVALID_JWT_TOKEN, "Token is not type access"
                )
            if require_fresh and not payload.get("fresh"):
                raise AppException(
                    ErrorCode.JWT_TOKEN_NOT_FRESH, "Require fresh access token"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCode.JWT_TOKEN_EXPIRED, "Access token has expired")
        except jwt.InvalidTokenError as e:
            raise AppException(
                ErrorCode.INVALID_JWT_TOKEN, "Invalid token refresh token"
            )


def get_jwt_service() -> JWTService:
    settings = get_settings()
    return JWTService(
        secret_key=settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_seconds=settings.JWT_ACCESS_TOKEN_EXPIRES,
        refresh_token_expire_seconds=settings.JWT_REFRESH_TOKEN_EXPIRES,
    )


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]


class JWTPayloadProvider:
    """
    A callable class for fastapi dependencies.
    Use to decode, validate and provide JWT token stored on cookie.

    Example:
        @router.get("/require_jwt_token")
        def func(
            jwt_access_payload: AccessToken,
            jwt_refresh_payload: RefreshToken,
        ):
            pass
    """

    def __init__(
        self,
        token_type: Literal["access", "refresh"] = "access",
        optional: bool = False,
        fresh: bool = False,
    ):
        """

        Args:
            token_type: "access" or "refresh"
            optional: if True return None when cookie not provided, otherwise raise AppException.
            fresh: Use for access_token only, if True access_token mus be fresh(if not fresh raises AppException).
        """

        self.token_type: Literal["access", "refresh"] = token_type
        self.optional: bool = optional
        self.fresh: bool = fresh

    def __call__(
        self, request: Request, jwt_service: JWTServiceDep
    ) -> JWTPayload | None:
        """
        Validates JWT token from request cookies and return payload as dict.
        If request cookies not provided and optional=False, raise AppException.
        Args:
            request: fastapi request object(auto-injected as dependency by fastapi)
            jwt_service: jwt service object(auto-injected as dependency by fastapi)

        Returns: JWTPayload

        """
        settings = get_settings()
        cookie_name = (
            settings.JWT_ACCESS_COOKIE_NAME
            if (self.token_type == "access")
            else settings.JWT_REFRESH_COOKIE_NAME
        )
        token = request.cookies.get(cookie_name)

        if not token:
            if self.optional:
                return None
            else:
                raise AppException(ErrorCode.UNAUTHORIZED, "Require JWT Cookie")

        payload = jwt_service.validate_token(token)

        if self.fresh and not payload.fresh:
            raise AppException(ErrorCode.JWT_TOKEN_NOT_FRESH, "Require fresh JWT token")

        if self.token_type != payload.token_type:
            raise AppException(
                ErrorCode.INVALID_JWT_TOKEN,
                f"Invalid token type. Expect '{self.token_type}' but got '{payload.token_type}' instead",
            )
        return payload


AccessToken = Annotated[JWTPayload, Depends(JWTPayloadProvider())]

FreshAccessToken = Annotated[JWTPayload, Depends(JWTPayloadProvider(fresh=True))]

OptionalAccessToken = Annotated[
    JWTPayload | None, Depends(JWTPayloadProvider(optional=True))
]

RefreshToken = Annotated[JWTPayload, Depends(JWTPayloadProvider(token_type="refresh"))]
