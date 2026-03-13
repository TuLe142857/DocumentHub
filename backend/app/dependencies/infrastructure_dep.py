from typing import Annotated, Generator

from fastapi import Depends
from mypy_boto3_s3 import S3Client
from redis import Redis
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.core import get_db_engine, get_redis, get_s3


def get_db_session() -> Generator[Session, None, None]:
    with Session(bind=get_db_engine()) as session:
        yield session


DBEngineDep = Annotated[Engine, Depends(get_db_engine)]

DBSessionDep = Annotated[Session, Depends(get_db_session)]

RedisDep = Annotated[Redis, Depends(get_redis)]

S3Dep = Annotated[S3Client, Depends(get_s3)]
