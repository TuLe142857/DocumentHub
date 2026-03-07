import boto3
from fastapi import Depends
from mypy_boto3_s3 import S3Client
from typing import Annotated
from app.core import settings

__s3_client: S3Client|None = None

def get_s3_client() -> S3Client:
    """
    Lazy load S3 client
    """
    global __s3_client
    if __s3_client is None:
        __s3_client = boto3.client(
            __name__,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY.get_secret_value(),
            endpoint_url=settings.S3_ENDPOINT
        )
    return __s3_client

S3Dep = Annotated[S3Client, Depends(get_s3_client)]