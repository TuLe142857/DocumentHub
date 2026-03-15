from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from redis import Redis, from_url

from app.core import get_settings


@lru_cache
def get_redis() -> Redis:
    settings = get_settings()
    return from_url(str(settings.REDIS_URL))


RedisDep = Annotated[Redis, Depends(get_redis)]
