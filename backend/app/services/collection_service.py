from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.crud.collection import CRUDCollection, CRUDCollectionDep
from app.dependencies import DBSessionDep
from app.models import *

from .access_control_service import AccessControlService, AccessControlServiceDep


class CollectionService:
    def __init__(
        self,
        crud_collection: CRUDCollection,
        access_control: AccessControlService,
        db_session: Session,
    ):
        self.crud_collection = crud_collection
        self.access_control = access_control
        self.db_session = db_session

    def list_collection(self, owner_id: int) -> Sequence[Collection]:
        return (
            self.db_session.execute(
                select(Collection).where(Collection.owner_id == owner_id)
            )
            .scalars()
            .all()
        )

    def create_collection(self, owner_id: int, name: str):
        if self.crud_collection.select(owner_id=owner_id, name=name) is not None:
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Collection already exists"
            )
        self.crud_collection.create(Collection(owner_id=owner_id, name=name))

    def list_document(self, user_id: int, collection_id: int) -> list[Document]:
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_view_collection(user_id, collection)
        if err is not None:
            raise err

        return [i.document for i in collection.items]

    def rename_collection(self, user_id: int, collection_id: int, new_name: str):
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_update_collection(user_id, collection)
        if err is not None:
            raise err

        self.crud_collection.update(collection, {"name": new_name})

    def add_document_to_collection(
        self, user_id: int, collection_id: int, document_id: int
    ):

        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_update_collection(user_id, collection)
        if err is not None:
            raise err
        self.crud_collection.add_document(collection, document_id)

    def remove_document_from_collection(
        self, user_id: int, collection_id: int, document_id: int
    ):
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_update_collection(user_id, collection)
        if err is not None:
            raise err

        self.crud_collection.remove_document(collection, document_id)

    def delete_collection(self, user_id: int, collection_id: int):
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_delete_collection(user_id, collection)
        if err is not None:
            raise err

        self.crud_collection.delete(collection)


def get_collection_service(
    crud_collection: CRUDCollectionDep,
    access_control: AccessControlServiceDep,
    db_session: DBSessionDep,
) -> CollectionService:
    return CollectionService(crud_collection, access_control, db_session)


CollectionServiceDep = Annotated[CollectionService, Depends(get_collection_service)]
