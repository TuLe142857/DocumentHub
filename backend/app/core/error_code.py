import enum


class ErrorCode(enum.Enum):
    def __init__(self, error_code: str, status_code: int):
        self.__error_code = error_code
        self.__status_code = status_code

    @property
    def error_code(self) -> str:
        return self.__error_code

    @property
    def status_code(self) -> int:
        return self.__status_code

    UNKNOWN_ERROR = ("UNKNOWN_ERROR", 500)
    SYSTEM_ERROR = ("SYSTEM_ERROR", 500)
