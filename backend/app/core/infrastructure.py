from functools import lru_cache

import boto3
from mypy_boto3_s3 import S3Client
from redis import Redis, from_url
from sqlalchemy import Engine, create_engine

from .config import get_settings


@lru_cache
def get_db_engine() -> Engine:
    return create_engine(str(get_settings().MYSQL_URL))


@lru_cache
def get_redis() -> Redis:
    return from_url(str(get_settings().REDIS_URL))


@lru_cache
def get_s3() -> S3Client:
    return boto3.client(
        "s3",
        aws_access_key_id=get_settings().S3_ACCESS_KEY,
        aws_secret_access_key=get_settings().S3_SECRET_KEY.get_secret_value(),
        endpoint_url=get_settings().S3_ENDPOINT,
    )
