from typing import Annotated, Generator

from fastapi import Depends
from mypy_boto3_s3 import S3Client
from redis import Redis
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.core import get_db_engine, get_redis, get_s3

DBEngineDep = Annotated[Engine, Depends(get_db_engine)]


def get_db_session(engine: DBEngineDep) -> Generator[Session, None, None]:
    with Session(bind=engine) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db_session)]

RedisDep = Annotated[Redis, Depends(get_redis)]

S3Dep = Annotated[S3Client, Depends(get_s3)]
