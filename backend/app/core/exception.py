from fastapi import FastAPI, Request

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
        - Exception: unexpected exception that had not been caught.

    Args:
        app: FastAPI app

    Returns:
        None
    """

    @app.exception_handler(AppException)
    def app_exception_handler(request: Request, exc: AppException) -> APIResponse:
        return APIResponse.error(exc.error_code, exc.message)

    @app.exception_handler(Exception)
    def unexpected_exception_handler(request: Request, exc: Exception) -> APIResponse:
        import logging

        logging.exception(exc)
        return APIResponse.error(ErrorCode.UNKNOWN_ERROR, "Something went wrong :)")
