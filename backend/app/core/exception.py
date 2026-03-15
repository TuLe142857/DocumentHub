from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.exc import IntegrityError

from .config import get_settings
from .error_code import ErrorCode
from .response import APIResponse


class AppException(Exception):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        message: str | None = None,
    ):
        self.__error_code = error_code
        self.__message = message

    @property
    def error_code(self) -> ErrorCode:
        return self.__error_code

    @property
    def message(self) -> str | None:
        return self.__message


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register the exception handlers. All exception handlers will return APIResponse.error().

    Exceptions that will be handled:
        - AppException: custom app exception.
        - IntegrityError: SQLAlchemy error.
        - RequestValidationError: override fastapi RequestValidationError handler.
        - HTTPException: override fastapi HTTPException handler.
        - Exception: unexpected exception that had not been caught.

    Args:
        app: FastAPI app

    Returns:
        None
    """

    @app.exception_handler(AppException)
    def app_exception_handler(request: Request, exc: AppException) -> APIResponse:
        return APIResponse.error(exc.error_code, exc.message)

    @app.exception_handler(IntegrityError)
    def sqlalchemy_integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> APIResponse:
        return APIResponse.error(ErrorCode.DATA_INTEGRITY_ERROR, str(exc))

    @app.exception_handler(RequestValidationError)
    def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> APIResponse:
        return APIResponse.error(ErrorCode.VALIDATION_ERROR, str(exc.errors()))

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException) -> APIResponse:
        return APIResponse.error(ErrorCode.UNKNOWN_ERROR, str(exc))

    @app.exception_handler(Exception)
    def unexpected_exception_handler(request: Request, exc: Exception) -> APIResponse:
        import logging

        logging.exception(exc)
        if get_settings().ENVIRONMENT == "prod":
            message = str(exc)
        else:
            message = "Something went wrong"
        return APIResponse.error(ErrorCode.UNKNOWN_ERROR, message)
