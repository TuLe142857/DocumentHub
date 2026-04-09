from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.dependencies import DBSessionDep
from app.models import Collection, CollectionItem

from .base import CRUDBase


class CRUDCollection(CRUDBase[Collection, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(model=Collection, db_session=db_session)

    def select(self, owner_id: int, name: str) -> Collection | None:
        return self.db_session.execute(
            select(Collection).where(
                and_(Collection.owner_id == owner_id, Collection.name == name)
            )
        ).scalar_one_or_none()

    def add_document(
        self,
        collection: Collection,
        document_id: int,
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> Collection:
        collection.items.append(CollectionItem(document_id=document_id))
        return self._save(collection, auto_commit=auto_commit, auto_flush=auto_flush)

    def remove_document(
        self,
        collection: Collection,
        document_id: int,
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> Collection:
        collection.items = [_ for _ in collection.items if _.document_id != document_id]
        return self._save(collection, auto_commit=auto_commit, auto_flush=auto_flush)


def get_crud_collection(db_session: DBSessionDep) -> CRUDCollection:
    return CRUDCollection(db_session=db_session)


CRUDCollectionDep = Annotated[CRUDCollection, Depends(get_crud_collection)]
