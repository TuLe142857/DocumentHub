from functools import lru_cache

import boto3
from mypy_boto3_s3 import S3Client

from app.core import get_settings


@lru_cache
def get_s3() -> S3Client:
    settings = get_settings()

    return boto3.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY.get_secret_value(),
        endpoint_url=settings.S3_ENDPOINT,
    )
