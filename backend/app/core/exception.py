from fastapi import FastAPI
from .error_code import ErrorCode


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
    pass
