from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.crud.collection import CRUDCollection, CRUDCollectionDep
from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep
from app.models import *


class AccessControlService:
    def __init__(
        self,
        crud_doc: CRUDDocument,
        crud_user: CRUDUser,
        crud_collection: CRUDCollection,
        db_session: Session,
    ):
        self.crud_doc = crud_doc
        self.crud_user = crud_user
        self.crud_collection = crud_collection
        self.db_session = db_session

    def can_view_by_non_owner(self, doc: int | Document) -> AppException | None:
        if isinstance(doc, int):
            document = self.crud_doc.get(doc)
            if document is None:
                return AppException(ErrorCode.RESOURCE_NOT_FOUND, "Document not found")
        else:
            document = doc

        if document.status == DocumentStatus.BANNED:
            return AppException(ErrorCode.RESOURCE_NOT_AVAILABLE, "Document is banned")
        elif document.status == DocumentStatus.DELETED:
            return AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document has been deleted"
            )
        elif document.status == DocumentStatus.PROCESSING:
            return AppException(
                ErrorCode.RESOURCE_NOT_AVAILABLE, "Document is processing"
            )

        if document.visibility == DocumentVisibility.PUBLIC:
            return None
        else:
            return AppException(ErrorCode.FORBIDDEN, "Document is not public")

    def can_view_document(
        self, user_id: int, doc: int | Document
    ) -> AppException | None:
        """

        Args:
            user_id: user id
            doc: document id or Document instance

        Returns:

        """
        if isinstance(doc, int):
            document = self.crud_doc.get(doc)
            if document is None:
                return AppException(ErrorCode.RESOURCE_NOT_FOUND, "Document not found")
        else:
            document = doc
        # owner
        if document.owner_id == user_id:
            return None

        return self.can_view_by_non_owner(document)

    def can_update_document(
        self, user_id: int, doc: int | Document
    ) -> AppException | None:
        if isinstance(doc, int):
            document = self.crud_doc.get(doc)
            if document is None:
                return AppException(ErrorCode.RESOURCE_NOT_FOUND, "Document not found")
        else:
            document = doc

        if document.owner_id == user_id:
            return None
        else:
            return AppException(ErrorCode.FORBIDDEN)

    def can_delete_document(
        self, user_id: int, doc: int | Document
    ) -> AppException | None:
        """
        Soft deletes document(move to trash)
        Args:
            user_id:
            doc:

        Returns:

        """
        if isinstance(doc, int):
            document = self.crud_doc.get(doc)
            if document is None:
                return AppException(ErrorCode.RESOURCE_NOT_FOUND, "Document not found")
        else:
            document = doc

        if document.owner_id == user_id:
            return None
        return AppException(ErrorCode.FORBIDDEN)

    def can_restore_document(
        self, user_id: int, doc: int | Document
    ) -> AppException | None:
        if isinstance(doc, int):
            document = self.crud_doc.get(doc)
            if document is None:
                return AppException(ErrorCode.RESOURCE_NOT_FOUND, "Document not found")
        else:
            document = doc
        if document.owner_id == user_id:
            return None
        return AppException(ErrorCode.FORBIDDEN)

    def can_ban_document(self, user_id: int, document_id: int) -> AppException | None:
        """
        For admin only.
        Args:
            user_id:
            document_id:

        Returns:

        """
        pass

    def can_unban_document(self, user_id: int, document_id: int) -> AppException | None:
        """
        For admin only.
        Args:
            user_id:
            document_id:

        Returns:

        """
        pass

    def can_view_collection(
        self, user_id: int, collection: int | Collection
    ) -> AppException | None:
        if isinstance(collection, int):
            collection = self.crud_collection.get(
                collection, on_not_found=AppException(ErrorCode.RESOURCE_NOT_FOUND)
            )
        if collection.owner_id != user_id:
            return AppException(ErrorCode.FORBIDDEN)
        return None

    def can_update_collection(
        self, user_id: int, collection: int | Collection
    ) -> AppException | None:
        if isinstance(collection, int):
            collection = self.crud_collection.get(
                collection, on_not_found=AppException(ErrorCode.RESOURCE_NOT_FOUND)
            )

        if collection.owner_id != user_id:
            return AppException(ErrorCode.FORBIDDEN)
        return None

    def can_delete_collection(
        self, user_id: int, collection: int | Collection
    ) -> AppException | None:
        if isinstance(collection, int):
            collection = self.crud_collection.get(
                collection, on_not_found=AppException(ErrorCode.RESOURCE_NOT_FOUND)
            )

        if collection.owner_id != user_id:
            return AppException(ErrorCode.FORBIDDEN)
        return None


def get_access_control_service(
    crud_doc: CRUDDocumentDep,
    crud_user: CRUDUserDep,
    crud_collection: CRUDCollectionDep,
    db_session: DBSessionDep,
):
    return AccessControlService(crud_doc, crud_user, crud_collection, db_session)


AccessControlServiceDep = Annotated[
    AccessControlService, Depends(get_access_control_service)
]
