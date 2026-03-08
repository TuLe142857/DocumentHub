from redis import Redis, from_url
from sqlalchemy.sql.annotation import Annotated
from fastapi import Depends
from app.core import settings


__redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Lazy load redis client
    """
    global __redis_client
    if __redis_client is None:
        __redis_client = from_url(str(settings.REDIS_URL))
    return __redis_client


RedisDeps = Annotated[Redis, Depends(get_redis_client)]
