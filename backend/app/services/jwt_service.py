import datetime

import jwt

from app.core import AppException, ErrorCode


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
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=int(self.access_token_expire_seconds)),
        }
        if claim:
            for key, value in claim.items():
                payload[key] = value
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_refresh_token(self, refresh_token: str) -> dict:
        """
        Raises AppException if the refresh token is invalid
        :param refresh_token: refresh token
        :return: payload as dict
        """
        try:
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithm=[self.algorithm]
            )
            if payload.get("type") != "refresh":
                raise AppException(ErrorCode.INVALID_TOKEN, "Token is not type refresh")
            return payload
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCode.TOKEN_EXPIRED, "Token has expired")
        except jwt.InvalidTokenError:
            raise AppException(ErrorCode.INVALID_TOKEN, "Invalid token")

    def validate_access_token_expired(self, access_token: str) -> dict:
        """
        Raises AppException if the access token is invalid
        :param access_token: access token
        :return: payload as dict
        """
        try:
            payload = jwt.decode(
                access_token, self.secret_key, algorithm=[self.algorithm]
            )
            if payload.get("type") != "access":
                raise AppException(ErrorCode.INVALID_TOKEN, "Token is not type access")
            return payload
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCode.TOKEN_EXPIRED, "Token has expired")
        except jwt.InvalidTokenError:
            raise AppException(ErrorCode.INVALID_TOKEN, "Invalid token")
