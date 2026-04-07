from typing import Annotated

from fastapi import Depends

from app.core import AppException, ErrorCode
from app.models import *


class AccessControlService:
    def __init__(self):
        pass

    def can_view_by_anyone(self, document: Document) -> AppException | None:
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

    def can_view_document(self, user: User, document: Document) -> AppException | None:
        """
        Check if user have permission to view the document
        Args:
            user: User
            document: Document

        Returns:

        """
        # owner
        if document.owner_id == user.id:
            return None
        return self.can_view_by_anyone(document)

    def can_download_document(
        self, user: User, document: Document
    ) -> AppException | None:
        return self.can_view_document(user, document)

    def can_update_document(
        self, user: User, document: Document
    ) -> AppException | None:
        if document.owner_id == user.id:
            return None
        else:
            return AppException(ErrorCode.FORBIDDEN)

    def can_delete_document(
        self, user: User, document: Document
    ) -> AppException | None:
        """
        Soft deletes document(move to trash)
        """
        if document.owner_id == user.id:
            return None
        return AppException(ErrorCode.FORBIDDEN)

    def can_restore_document(
        self, user: User, document: Document
    ) -> AppException | None:
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

    def can_view_collection(
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
