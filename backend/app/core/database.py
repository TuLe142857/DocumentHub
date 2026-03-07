from sqlalchemy import Engine, create_engine
from .config import settings

__db_engine: Engine | None = None


def get_db_engine() -> Engine:
    global __db_engine
    if __db_engine is None:
        __db_engine = create_engine(str(settings.MYSQL_URL))
    return __db_engine
