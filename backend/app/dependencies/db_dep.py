from sqlalchemy.orm import Session
from typing import Annotated, Generator
from fastapi import Depends
from app.core import get_db_engine

def get_db_session()-> Generator[Session, None, None]:
    with Session(bind=get_db_engine()) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_db_session)]
