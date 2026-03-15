from functools import lru_cache

from sqlalchemy import Engine, create_engine

from app.core import get_settings


@lru_cache
def get_db_engine() -> Engine:
    settings = get_settings()
    return create_engine(str(settings.MYSQL_URL))
