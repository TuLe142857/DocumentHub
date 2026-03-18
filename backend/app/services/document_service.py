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
from app.tasks import generate_document_preview_task
from app.utils import md5_checksum, sha256_checksum


class DocumentService:
    def __init__(
        self,
        crud_doc: CRUDDocument,
        crud_user: CRUDUser,
        access_control: AccessControlService,
        db_session: Session,
        redis_client: Redis,
        s3_client: S3Client,
    ):

        self.crud_doc = crud_doc
        self.crud_user = crud_user
        self.access_control = access_control
        self.db_session = db_session
        self.redis_client = redis_client
        self.s3_client = s3_client

    def get_document_by_owner_id(
        self, owner_id: int, page: int, limit: int
    ) -> tuple[Sequence[Document], int]:
        skip = (page - 1) * limit
        return self.crud_doc.get_multi(
            Document.owner_id == owner_id,
            skip=skip,
            limit=limit,
        )

    def get_public_document_list(
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
            return self.get_public_document_list(owner_id, page, limit)
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

    def select_document_by_user(self, user_id: int, document_id: int) -> Document:
        err = self.access_control.can_view_document(user_id, document_id)
        if err:
            raise err
        return self.db_session.execute(
            select(Document).where(Document.id == document_id)
        ).scalar_one_or_none()

    def update_document(
        self, user_id: int, document_id: int, update_data: dict[str, Any]
    ):
        err = self.access_control.can_update_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.update(self.crud_doc.get(document_id), update_data)

    def add_tags_to_document(self, document_id: int, user_id: int, tags: list[str]):
        err = self.access_control.can_update_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.add_tags(self.crud_doc.get(document_id), tags)

    def remove_tags_from_document(
        self, document_id: int, user_id: int, tags: list[str]
    ):
        err = self.access_control.can_update_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.remove_tags(self.crud_doc.get(document_id), tags)

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

    def get_trash_list(self, user_id: int) -> list[Document]:
        return self.crud_doc.get_trash_list(user_id)

    def restore_document(self, document_id: int, user_id: int):
        err = self.access_control.can_view_document(user_id, document_id)
        if err:
            raise err
        self.crud_doc.restore_document_from_trash(self.crud_doc.get(document_id))


def get_document_service(
    crud_doc: CRUDDocumentDep,
    crud_user: CRUDUserDep,
    access_control: AccessControlServiceDep,
    db_session: DBSessionDep,
    redis_client: RedisDep,
    s3_client: S3Dep,
) -> DocumentService:
    return DocumentService(
        crud_doc, crud_user, access_control, db_session, redis_client, s3_client
    )


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
