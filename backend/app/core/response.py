from datetime import datetime
from typing import Any, Generic, Literal, Mapping, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from .config import settings
from .error_code import ErrorCode

T = TypeVar("T")


class ResponseSuccessSchema(BaseModel, Generic[T]):
    success: Literal[True]
    data: T
    message: str | None


class ResponseErrorSchema(BaseModel):
    success: Literal[False]
    error_code: str
    message: str | None


class APIResponse(JSONResponse):
    """
    Use:
        ApiResponse.ok() for success response(JSON body will be built as  ResponseSuccessSchema).
        ApiResponse.error() for error response(JSON body will be built as  ResponseErrorSchema).
    """

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Copy from supper class __init__.
        Do not use this.
        Use APIResponse.ok() or APIResponse.error() instead.
        """
        super().__init__(content, status_code, headers, media_type, background)

    @staticmethod
    def ok(
        data: Any = None, message: str | None = None, status_code: int = 200
    ) -> "APIResponse":
        """
        Build JSON response for success response.
        Body will be built as ResponseSuccessSchema.
        """
        body = {
            "success": True,
            "data": jsonable_encoder(data),
            "message": message,
        }
        return APIResponse(content=body, status_code=status_code)

    @staticmethod
    def error(
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR, message: str | None = None
    ) -> "APIResponse":
        """
        Build JSON response for error response.
        Body will be built as ResponseErrorSchema.
        """
        body = {
            "success": False,
            "error_code": error_code.error_code,
            "message": message,
        }
        return APIResponse(
            content=body,
            status_code=error_code.status_code,
        )

    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: int | None = None,
        expires: datetime | str | int | None = None,
        path: str | None = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
        partitioned: bool = False,
    ) -> "APIResponse":
        """
        This method call super().set_cookie() but return self for builder pattern.
        """
        super().set_cookie(
            key,
            value,
            max_age,
            expires,
            path,
            domain,
            secure,
            httponly,
            samesite,
            partitioned,
        )
        return self

    def delete_cookie(
        self,
        key: str,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
    ) -> "APIResponse":
        """
        This method call super().delete_cookie() but return self for builder pattern.
        """
        super().delete_cookie(key, path, domain, secure, httponly, samesite)
        return self

    def set_access_cookie(self, access_token: str) -> "APIResponse":
        return self.set_cookie(
            key=settings.JWT_ACCESS_COOKIE_NAME,
            value=access_token,
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRES,
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path=settings.JWT_ACCESS_COOKIE_PATH,
        )

    def delete_access_cookie(self) -> "APIResponse":
        return self.delete_cookie(
            key=settings.JWT_ACCESS_COOKIE_NAME,
            path=settings.JWT_ACCESS_COOKIE_PATH,
            secure=settings.JWT_COOKIE_SECURE,
            httponly=True,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

    def set_refresh_cookie(self, refresh_token: str) -> "APIResponse":
        return self.set_cookie(
            key=settings.JWT_REFRESH_COOKIE_NAME,
            value=refresh_token,
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRES,
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path=settings.JWT_REFRESH_COOKIE_PATH,
        )

    def delete_refresh_cookie(self) -> "APIResponse":
        return self.delete_cookie(
            key=settings.JWT_REFRESH_COOKIE_NAME,
            path=settings.JWT_REFRESH_COOKIE_PATH,
            secure=settings.JWT_COOKIE_SECURE,
            httponly=True,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

    def set_header(self, key: str, value: str) -> "APIResponse":
        self.headers[key] = value
        return self
