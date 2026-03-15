from functools import lru_cache

from redis import Redis, from_url

from app.core import get_settings


@lru_cache
def get_redis() -> Redis:
    settings = get_settings()
    return from_url(str(settings.REDIS_URL))
