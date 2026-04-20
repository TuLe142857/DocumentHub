from typing import Annotated

from fastapi import Depends

from app.core import AppException, ErrorCode
from app.models import *


class AccessControlService:
    def __init__(self):
        pass

    def can_access_by_anyone(self, document: Document) -> AppException | None:
        """
        Check if this document is public and can be access by anyone
        Args:
            document:

        Returns:
            Return None if this document is public and can be access by anyone else return AppException.
            Available ErrorCode can be return with AppException:

            - ErrorCode.RESOURCE_NOT_AVAILABLE: This document currently is processing/banned/deleted(soft delete). This
              ErrorCode come with message to explain document status.

            - ErrorCode.FORBIDDEN: This document is not public
        """
        if document.visibility == DocumentVisibility.PRIVATE:
            return AppException(ErrorCode.FORBIDDEN, "Document is not public")

        if document.status == DocumentStatus.BANNED:
            return AppException(ErrorCode.RESOURCE_NOT_AVAILABLE, "Document is banned")
        elif document.status == DocumentStatus.DELETED:
            return AppException(
                ErrorCode.RESOURCE_NOT_AVAILABLE, "Document has been deleted"
            )
        elif document.status == DocumentStatus.PROCESSING:
            return AppException(
                ErrorCode.RESOURCE_NOT_AVAILABLE, "Document is processing"
            )

        return None

    def can_access_document(
        self, user: User, document: Document
    ) -> AppException | None:
        """
        Check if user have permission to access the document
        Args:
            user: User
            document: Document
        Returns:
            Return None if user has permission to access the document, else return AppException.
            Available ErrorCode can be return with AppException:

            - ErrorCode.RESOURCE_NOT_AVAILABLE:
            - ErrorCode.FORBIDDEN:
        """
        # owner
        if document.owner_id == user.id:
            return None
        return self.can_access_by_anyone(document)

    def can_update_document(
        self, user: User, document: Document
    ) -> AppException | None:
        """
        Check if user have permission to update the document(Check user is owner of the document)
        Args:
            user:
            document:

        Returns:
            Return None if user has permission to update the document, else return AppException.
            Available ErrorCode can be return with AppException:

            - ErrorCode.FORBIDDEN:

        """
        if document.owner_id == user.id:
            return None
        else:
            return AppException(ErrorCode.FORBIDDEN)

    def can_delete_document(
        self, user: User, document: Document
    ) -> AppException | None:
        """
        For owner only.
        Args:
            user:
            document:

        Returns:
            Return None if user has permission to delete the document, else return AppException.
            Available ErrorCode can be return with AppException:

            - ErrorCode.FORBIDDEN:

        """
        if document.owner_id == user.id:
            return None
        return AppException(ErrorCode.FORBIDDEN)

    def can_restore_document(
        self, user: User, document: Document
    ) -> AppException | None:
        """
        For owner only.
        Args:
            user:
            document:

        Returns:
            Return None if user has permission to restore the document, else return AppException.
            Available ErrorCode can be return with AppException:

            - ErrorCode.FORBIDDEN:

        """
        if document.owner_id == user.id:
            return None
        return AppException(ErrorCode.FORBIDDEN)

    def can_ban_document(self, user: User, document: Document) -> AppException | None:
        """
        For admin only.
        """
        if user.role.name == "ADMIN":
            return None
        if document.banned_at is not None:
            return AppException(ErrorCode.ACTION_CONFLICT, "Document is banned")
        return AppException(ErrorCode.FORBIDDEN)

    def can_unban_document(self, user: User, document: Document) -> AppException | None:
        """
        For admin only.
        """
        if user.role.name == "ADMIN":
            return None
        if document.banned_at is None:
            return AppException(ErrorCode.ACTION_CONFLICT, "Document is not banned")
        return AppException(ErrorCode.FORBIDDEN)

    def can_access_collection(
        self, user: User, collection: Collection
    ) -> AppException | None:
        if collection.owner_id != user.id:
            return AppException(ErrorCode.FORBIDDEN)
        return None

    def can_update_collection(
        self, user: User, collection: Collection
    ) -> AppException | None:
        if collection.owner_id != user.id:
            return AppException(ErrorCode.FORBIDDEN)
        return None

    def can_delete_collection(
        self, user: User, collection: Collection
    ) -> AppException | None:
        if collection.owner_id != user.id:
            return AppException(ErrorCode.FORBIDDEN)
        return None


def get_access_control_service():
    return AccessControlService()


AccessControlServiceDep = Annotated[
    AccessControlService, Depends(get_access_control_service)
]
