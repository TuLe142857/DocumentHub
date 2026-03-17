from fastapi import FastAPI

from .limit_upload_size import LimitUploadSizeMiddleware


def register_middleware(app: FastAPI):
    from app.core import get_settings
    app.add_middleware(LimitUploadSizeMiddleware, max_file_size_byte=get_settings().MAX_FILE_SIZE)
