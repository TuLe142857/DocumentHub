from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.crud.collection import CRUDCollection, CRUDCollectionDep
from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.dependencies import DBSessionDep
from app.models import *

from .access_control_service import AccessControlService, AccessControlServiceDep


class CollectionService:
    def __init__(
        self,
        crud_collection: CRUDCollection,
        crud_doc: CRUDDocument,
        access_control: AccessControlService,
        db_session: Session,
    ):
        self.crud_collection = crud_collection
        self.crud_doc = crud_doc
        self.access_control = access_control
        self.db_session = db_session

    def list_collection(
        self,
        owner_id: int,
        keyword: str | None = None,
        document_id: int = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[Sequence[Collection], int]:
        """

        Args:
            owner_id:
            keyword:
            document_id: collection must contain this item
            page:
            limit:

        Returns:

        """
        # where_clauses = [Collection.owner_id == owner_id]
        # if keyword is not None:
        #     where_clauses.append(Collection.name.ilike(f"%{keyword.strip()}%"))
        # return self.crud_collection.get_multi(
        #     *where_clauses, skip=(page - 1) * limit, limit=limit
        # )

        stmt = select(Collection).where(Collection.owner_id == owner_id)
        if keyword is not None:
            stmt = stmt.where(Collection.name.ilike(f"%{keyword.strip()}%"))
        if document_id is not None:
            stmt = stmt.join(CollectionItem).where(
                CollectionItem.document_id == document_id
            )

        total = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )
        if total == 0:
            return list(), total

        stmt = stmt.offset((page - 1) * limit).limit(limit)
        res = self.db_session.execute(stmt).scalars().all()
        return res, total

    def create_collection(self, owner_id: int, name: str):
        """
        Create new collections
        Args:
            owner_id:
            name:

        Returns:

        Raises:
            ErrorCode.RESOURCE_ALREADY_EXISTS: collection name already exists

        """
        if self.crud_collection.select(owner_id=owner_id, name=name) is not None:
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Collection already exists"
            )
        self.crud_collection.create(Collection(owner_id=owner_id, name=name))

    def list_document(
        self,
        user: User,
        collection_id: int,
        keyword: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[Sequence[Document], int]:
        """

        Args:
            user:
            collection_id:
            keyword:
            page:
            limit:

        Returns:

        Raises:
            ErrorCode.RESOURCE_NOT_FOUND: collection not found
        """
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_access_collection(user, collection)
        if err is not None:
            raise err

        stmt = (
            select(Document)
            .join(CollectionItem)
            .where(CollectionItem.collection_id == collection_id)
        )
        if keyword is not None:
            stmt = stmt.where(Document.title.ilike(f"%{keyword.strip()}%"))

        count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )

        if count == 0:
            return [], count

        res = (
            self.db_session.execute(stmt.offset((page - 1) * limit).limit(limit))
            .scalars()
            .all()
        )
        return res, count

    def rename_collection(self, user: User, collection_id: int, new_name: str):
        """

        Args:
            user:
            collection_id:
            new_name:

        Returns:

        Raises:
            ErrorCode.RESOURCE_NOT_FOUND: collection not found
            ErrorCode.RESOURCE_ALREADY_EXISTS: Collection new_name already exists
            ErrorCode.FORBIDDEN: User not have permission to update collection
        """
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )
        err = self.access_control.can_update_collection(user, collection)
        if err is not None:
            raise err

        if collection.name == new_name:
            return
        if (
            self.db_session.execute(
                select(Collection).where(Collection.name == new_name)
            ).scalar_one_or_none()
            is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Collection name already exists"
            )

        self.crud_collection.update(collection, {"name": new_name})

    def add_document_to_collection(
        self, user: User, collection_id: int, document_id: int
    ):
        """

        Args:
            user:
            collection_id:
            document_id:

        Returns:
        Raises:
            ErrorCode.RESOURCE_NOT_FOUND: collection/document not found
            ErrorCode.FORBIDDEN: user does not have permission do to this action
        """
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_update_collection(
            user, collection
        ) or self.access_control.can_access_document(user, document)
        if err is not None:
            raise err

        self.crud_collection.add_document(collection, document_id)

    def sync_document_collections(
        self, user: User, document_id, collection_ids: list[int]
    ):
        """

        Args:
            user:
            document_id:
            collection_ids:

        Returns:
        Raises:
            ErrorCode.RESOURCE_NOT_FOUND: collection/document not found
            ErrorCode.FORBIDDEN: user does not have permission do to this action
        """
        collections = [
            self.crud_collection.get(
                collection_id,
                on_not_found=AppException(
                    ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
                ),
            )
            for collection_id in set(collection_ids)
        ]

        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        # check permission
        err = self.access_control.can_access_document(user, document)
        if err:
            raise err

        for collection in collections:
            err = self.access_control.can_update_collection(user, collection)
            if err:
                raise err

        document.collection_items = []
        document.collection_items = [
            CollectionItem(collection_id=c.id) for c in collections
        ]
        self.db_session.flush()

    def remove_document_from_collection(
        self, user: User, collection_id: int, document_id: int
    ):
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )
        self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_update_collection(user, collection)
        if err is not None:
            raise err

        self.crud_collection.remove_document(collection, document_id)

    def delete_collection(self, user: User, collection_id: int):
        """

        Args:
            user:
            collection_id:

        Returns:
        Raises:
            ErrorCode.RESOURCE_NOT_FOUND: Collection not found
            ErrorCode.FORBIDDEN: User not have permission to delete collection
        """
        collection = self.crud_collection.get(
            collection_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Collection not found"
            ),
        )

        err = self.access_control.can_delete_collection(user, collection)
        if err is not None:
            raise err

        self.crud_collection.delete(collection)


def get_collection_service(
    crud_collection: CRUDCollectionDep,
    crud_doc: CRUDDocumentDep,
    access_control: AccessControlServiceDep,
    db_session: DBSessionDep,
) -> CollectionService:
    return CollectionService(crud_collection, crud_doc, access_control, db_session)


CollectionServiceDep = Annotated[CollectionService, Depends(get_collection_service)]
