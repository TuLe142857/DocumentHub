from typing import Annotated, Generator

import boto3
from fastapi import Depends
from mypy_boto3_s3 import S3Client
from redis import Redis, from_url
from sqlalchemy.orm import Session

from app.core import get_db_engine, get_settings


def get_db_session() -> Generator[Session, None, None]:
    with Session(bind=get_db_engine()) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]

__redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Lazy load redis client
    """
    global __redis_client
    if __redis_client is None:
        __redis_client = from_url(str(get_settings().REDIS_URL))
    return __redis_client


RedisDep = Annotated[Redis, Depends(get_redis_client)]

__s3_client: S3Client | None = None


def get_s3_client() -> S3Client:
    """
    Lazy load S3 client
    """
    global __s3_client
    if __s3_client is None:
        __s3_client = boto3.client(
            __name__,
            aws_access_key_id=get_settings().S3_ACCESS_KEY,
            aws_secret_access_key=get_settings().S3_SECRET_KEY.get_secret_value(),
            endpoint_url=get_settings().S3_ENDPOINT,
        )
    return __s3_client


S3Dep = Annotated[S3Client, Depends(get_s3_client)]
