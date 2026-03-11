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

    # System (500)
    UNKNOWN_ERROR = ("UNKNOWN_ERROR", 500)
    SYSTEM_ERROR = ("SYSTEM_ERROR", 500)

    # Auth (401)
    UNAUTHORIZED = ("UNAUTHORIZED_ERROR", 401)
    TOKEN_EXPIRED = ("TOKEN_EXPIRED", 401)
    INVALID_TOKEN = ("INVALID_TOKEN", 401)

    # Permission (403)
    FORBIDDEN = ("FORBIDDEN", 403)

    # Client input (400)
    BAD_REQUEST = ("BAD_REQUEST", 400)

    # Resource
    RESOURCE_NOT_FOUND = ("RESOURCE_NOT_FOUND", 404)
    RESOURCE_ALREADY_EXISTS = ("RESOURCE_ALREADY_EXISTS", 409)
    RESOURCE_CONFLICT = ("RESOURCE_CONFLICT", 409)

    # Rate limit
    RATE_LIMIT_EXCEEDED = ("RATE_LIMIT_EXCEEDED", 429)

    # Database
    DATA_INTEGRITY_ERROR = ("DATA_INTEGRITY_ERROR", 409)

    # File
    FILE_TOO_LARGE = ("FILE_TOO_LARGE", 413)
    UNSUPPORTED_FILE_TYPE = ("UNSUPPORTED_FILE_TYPE", 415)
