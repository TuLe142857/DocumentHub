import datetime
from typing import Annotated, Any, BinaryIO, Sequence
import uuid

from fastapi import Depends
from mypy_boto3_s3 import S3Client
from redis import Redis
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode, get_settings
from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep, RedisDep, S3Dep
from app.models import *
from app.services.access_control_service import (
    AccessControlService,
    AccessControlServiceDep,
)
from app.services.storage_service import StorageService, StorageServiceDep
from app.tasks import generate_document_preview_task
from app.utils import md5_checksum, sha256_checksum


class DocumentService:
    def __init__(
        self,
        crud_doc: CRUDDocument,
        crud_user: CRUDUser,
        access_control: AccessControlService,
        storage_service: StorageService,
        db_session: Session,
        redis_client: Redis,
        s3_client: S3Client,
    ):

        self.crud_doc = crud_doc
        self.crud_user = crud_user
        self.access_control = access_control
        self.storage_service = storage_service
        self.db_session = db_session
        self.redis_client = redis_client
        self.s3_client = s3_client

    def list_self_documents(
        self, owner_id: int, page: int, limit: int, status: DocumentStatus | None = None
    ) -> tuple[Sequence[Document], int]:
        skip = (page - 1) * limit
        if status is None:
            return self.crud_doc.get_multi(
                Document.owner_id == owner_id,
                skip=skip,
                limit=limit,
            )
        else:
            return self.crud_doc.get_multi(
                Document.owner_id == owner_id,
                Document.status == status,
                skip=skip,
                limit=limit,
            )

    def list_public_document(
        self, owner: int | str | User, page: int, limit: int
    ) -> tuple[Sequence[Document], int]:
        if isinstance(owner, User):
            owner_id = owner.id
        elif isinstance(owner, str):
            owner_id = self.crud_user.get_by_identity(owner).id
        else:
            owner_id = owner

        return self.crud_doc.get_multi(
            Document.owner_id == owner_id,
            Document.status == DocumentStatus.READY,
            Document.visibility == DocumentVisibility.PUBLIC,
            skip=(page - 1) * limit,
            limit=limit,
        )

    def get_document_list(
        self, owner: int | str | User, viewer: int | User, page: int, limit: int
    ) -> tuple[Sequence[Document], int]:
        """
        Select documents that belong to a specific owner.
        If viewer
        Args:
            owner: owner of the documents. This can be instance User or user_id(int) or username/email(str)
            viewer: the user that query this list. This can be instance User or user_id(int) or username/email(str)
            page:
            limit:

        Returns:
        """
        if isinstance(owner, User):
            owner_id = owner.id
        elif isinstance(owner, str):
            owner_id = self.crud_user.get_by_identity(owner).id
        else:
            owner_id = owner

        if isinstance(viewer, User):
            viewer_id = viewer.id
        else:
            viewer_id = viewer

        if viewer_id != owner_id:
            return self.list_public_document(owner_id, page, limit)
        return self.crud_doc.get_multi(
            Document.owner_id == owner_id,
            Document.status == DocumentStatus.READY,
            skip=(page - 1) * limit,
            limit=limit,
        )

    def create_document(
        self,
        owner_id: int,
        title: str,
        category_id: int,
        visibility: DocumentVisibility,
        desc: str | None,
        tags: list[str],
        file: BinaryIO,
        file_type: str,
        content_type: str,
    ):
        random_uuid = str(uuid.uuid4())
        file_original_key = f"{random_uuid}/original"
        file_preview_key = f"{random_uuid}/preview"
        thumbnail_key = f"{random_uuid}/thumbnail"

        new_document = Document(
            owner_id=owner_id,
            category_id=category_id,
            status=DocumentStatus.PROCESSING,
            file_object_key=file_original_key,
            file_preview_object_key=file_preview_key,
            thumbnail_object_key=thumbnail_key,
            title=title,
            desc=desc,
            visibility=visibility,
            file_type=file_type,
            sha256sum=sha256_checksum(file),
            md5sum=md5_checksum(file),
        )
        self.db_session.add(new_document)

        # remove duplicate
        tags = list(set(tags))

        for tag_name in tags:
            new_document.tags.append(Tag.get_or_create(tag_name, self.db_session))

        self.s3_client.upload_fileobj(
            file,
            get_settings().S3_DOCUMENTS_BUCKET,
            new_document.file_object_key,
            ExtraArgs={
                "ContentType": content_type,
            },
        )

        self.db_session.commit()

        # finish create document & insert to database
        # call task to generate preview version(pdf) for document
        generate_document_preview_task.delay(document_id=new_document.id)

    def view_document(self, user_id: int | None, document_id: int) -> Document:
        """
        Check permission and return document.
        Increase document view.
        """
        err = self.access_control.can_view_document(user_id, document_id)
        if err:
            raise err

        doc: Document = self.db_session.execute(
            select(Document).where(Document.id == document_id)
        ).scalar_one_or_none()

        # increase view
        redis_view_key = f"view:doc:{document_id}:user:{user_id}"
        if self.redis_client.set(redis_view_key, "1", ex=3600, nx=True):
            doc.view_count += 1
            self.db_session.flush()
        return doc

    def download_document(
        self, user_id: int, document_id: int, document_format: str = ".pdf"
    ) -> str:
        """
        Check permission and return download url. Increase download count.
        Returns: document presigned url for download
        """
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_view_document(user_id, document)
        if err:
            raise err
        available_formats = {".pdf", document.file_type}
        if not (document_format in available_formats):
            raise AppException(
                ErrorCode.UNSUPPORTED_FILE_TYPE,
                f"Invalid document format for download. Available formats: {available_formats}",
            )

        redis_download_key = f"download:doc:{document_id}:user:{user_id}"
        if self.redis_client.set(redis_download_key, "1", ex=3600, nx=True):
            document.download_count += 1
            self.db_session.flush()

        ori_url, pdf_url = self.storage_service.generate_download_url_for_document(
            document
        )

        if document_format == ".pdf":
            return pdf_url
        return ori_url

    def is_liked(self, document_id: int, user_id: int):
        """
        Check if document is liked by a specified user.
        """
        return (
            self.db_session.execute(
                select(DocumentLike).where(
                    DocumentLike.document_id == document_id,
                    DocumentLike.user_id == user_id,
                )
            ).scalar_one_or_none()
            is not None
        )

    def update_document(
        self,
        user_id: int,
        document_id: int,
        desc: str | None = None,
        title: str | None = None,
        category_id: int | None = None,
        visibility: DocumentVisibility | None = None,
        tags: list[str] | None = None,
    ):
        """
        Any param left default None value will be ignored.
        """

        err = self.access_control.can_update_document(user_id, document_id)
        if err:
            raise err
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )
        update_dict = {}
        if desc:
            update_dict["desc"] = desc
        if title:
            update_dict["title"] = title
        if category_id:
            update_dict["category_id"] = category_id
        if visibility:
            update_dict["visibility"] = visibility

        if tags:
            unique_tags = set(tags)
            tags_override = [
                Tag.get_or_create(name, self.db_session) for name in unique_tags
            ]
            document.tags = tags_override

        self.crud_doc.update(document, update_dict)

    def add_tag_to_document(self, document_id: int, user_id: int, tag_name: str):
        err = self.access_control.can_update_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.add_tags(self.crud_doc.get(document_id), [tag_name])

    def remove_tag_from_document(self, document_id: int, user_id: int, tag_name: str):
        err = self.access_control.can_update_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.remove_tags(self.crud_doc.get(document_id), [tag_name])

    def like_document(self, document_id: int, user_id: int):
        err = self.access_control.can_view_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.add_like(self.crud_doc.get(document_id), user_id)

    def unlike_document(self, document_id: int, user_id: int):
        err = self.access_control.can_view_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.remove_like(self.crud_doc.get(document_id), user_id)

    def soft_delete_document(self, document_id: int, user_id: int):
        err = self.access_control.can_delete_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.soft_delete(self.crud_doc.get(document_id))

    # def get_trash_list(self, user_id: int) -> Sequence[Document]:
    #     return (
    #         self.db_session.execute(
    #             select(Document).where(
    #                 Document.owner_id == user_id, Document.deleted_at != None
    #             )
    #         )
    #         .scalars()
    #         .all()
    #     )

    def restore_document(self, document_id: int, user_id: int):
        err = self.access_control.can_restore_document(user_id, document_id)
        if err:
            raise err
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )
        if document.deleted_at is None:
            raise AppException(ErrorCode.RESOURCE_CONFLICT, "Document is not deleted")
        document.deleted_at = None
        if document.banned_at is not None:
            document.status = DocumentStatus.BANNED
        else:
            document.status = DocumentStatus.READY
        self.db_session.add(document)

    def ban_document(self, document_id: int, admin_id: int, note: str | None = None):
        err = self.access_control.can_ban_document(admin_id, document_id)
        if err:
            raise err
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )
        if document.status == DocumentStatus.BANNED:
            raise AppException(
                ErrorCode.RESOURCE_CONFLICT, "Document is already banned"
            )

        document.status = DocumentStatus.BANNED
        document.banned_at = datetime.datetime.now(datetime.timezone.utc)
        moderation_log = ModerationLog(
            document_id=document_id,
            admin_id=admin_id,
            action=ModerationAction.BAN_DOCUMENT,
            note=note,
        )

        self.db_session.add(document)
        self.db_session.add(moderation_log)

    def unban_document(self, document_id: int, admin_id: int, note: str | None = None):
        err = self.access_control.can_unban_document(admin_id, document_id)
        if err:
            raise err
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )
        if document.status != DocumentStatus.BANNED:
            raise AppException(ErrorCode.RESOURCE_CONFLICT, "Document not banned")

        if document.deleted_at is None:
            document.status = DocumentStatus.READY
        else:
            document.status = DocumentStatus.DELETED

        document.banned_at = None
        moderation_log = ModerationLog(
            document_id=document_id,
            admin_id=admin_id,
            action=ModerationAction.UNBAN_DOCUMENT,
            note=note,
        )

        self.db_session.add(document)
        self.db_session.add(moderation_log)

    def create_category(self, name: str):
        if (
            self.db_session.execute(
                select(Category).where(Category.name == name)
            ).scalar_one_or_none()
            is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Category already exists"
            )
        category = Category(name=name)
        self.db_session.add(category)

    def rename_category(self, category_id: int, new_name: str):
        category = self.db_session.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        if category is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category does not exist")
        if (
            self.db_session.execute(
                select(Category).where(Category.name == new_name)
            ).scalar_one_or_none()
            is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Category already exists"
            )
        category.name = new_name
        self.db_session.add(category)

    def delete_category(self, category_id: int):
        is_used = self.db_session.execute(
            select(Document).where(Document.category_id == category_id)
        ).scalar_one_or_none()

        if is_used:
            raise AppException(ErrorCode.RESOURCE_IN_USE, "Category is in use")
        category = self.db_session.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        if category is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category does not exist")
        self.db_session.delete()


def get_document_service(
    crud_doc: CRUDDocumentDep,
    crud_user: CRUDUserDep,
    access_control: AccessControlServiceDep,
    storage_service: StorageServiceDep,
    db_session: DBSessionDep,
    redis_client: RedisDep,
    s3_client: S3Dep,
) -> DocumentService:
    return DocumentService(
        crud_doc,
        crud_user,
        access_control,
        storage_service,
        db_session,
        redis_client,
        s3_client,
    )


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
