from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import DBSessionDep
from app.models import Collection

from .base import CRUDBase


class CRUDCollection(CRUDBase[Collection, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(model=Collection, db_session=db_session)


def get_crud_collection(db_session: DBSessionDep) -> CRUDCollection:
    return CRUDCollection(db_session=db_session)


CRUDCollectionDep = Annotated[CRUDCollection, Depends(get_crud_collection)]
