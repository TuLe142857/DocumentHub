from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core import get_settings


@lru_cache
def get_db_engine() -> Engine:
    settings = get_settings()
    return create_engine(str(settings.MYSQL_URL))


DBEngineDep = Annotated[Engine, Depends(get_db_engine)]


def get_db_session(engine: DBEngineDep):
    with Session(bind=engine) as session:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise  # raise exception for exception handler to catch


DBSessionDep = Annotated[Session, Depends(get_db_session)]
