from datetime import datetime

from pydantic import BaseModel
from typing import Generic, TypeVar, Literal, Any, Mapping

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.background import BackgroundTask

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
        User APIResponse.ok() or APIResponse.error() instead.
        """
        super().__init__(content, status_code, headers, media_type, background)

    @staticmethod
    def ok(
        data: Any = None, message: str | None = None, status_code: int = 200
    ) -> "APIResponse":
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
        super().delete_cookie(key, path, domain, secure, httponly, samesite)
        return self

    def set_header(self, key: str, value: str) -> "APIResponse":
        self.headers[key] = value
