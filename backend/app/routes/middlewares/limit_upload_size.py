from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.types import ASGIApp

from app.core import APIResponse, ErrorCode


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_file_size_byte: int) -> None:
        super().__init__(app)
        self.max_file_size_byte = max_file_size_byte

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "POST":
            if "content-length" in request.headers:
                content_length = int(request.headers.get("content-length"))
                if content_length > self.max_file_size_byte:
                    return APIResponse.error(
                        ErrorCode.FILE_TOO_LARGE,
                        f"File too large({content_length}). Max supported file size = {self.max_file_size_byte}",
                    )
        response = await call_next(request)
        return response
