from typing import Annotated, BinaryIO, Sequence
import uuid

from fastapi import Depends
from mypy_boto3_s3 import S3Client
from redis import Redis
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode, get_settings
from app.dependencies import DBSessionDep, RedisDep, S3Dep
from app.models import *
from app.tasks import generate_document_preview_task
from app.utils import md5_checksum, sha256_checksum


class DocumentService:
    def __init__(self, db_session: Session, redis_client: Redis, s3_client: S3Client):
        self.db_session = db_session
        self.redis_client = redis_client
        self.s3_client = s3_client

    def get_document_by_owner_id(self, owner_id: int) -> Sequence[Document]:
        return (
            self.db_session.execute(
                select(Document).where(Document.owner_id == owner_id)
            )
            .scalars()
            .all()
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

        self.db_session.add(new_document)
        self.db_session.commit()

        # finish create document & insert to database
        # call task to generate preview version(pdf) for document
        generate_document_preview_task.delay(document_id=new_document.id)

    # def check_access_permission(self, document_id: int, user_id: int) -> bool:
    #     document = self.db_session.execute(
    #         select(Document).where(Document.id == document_id)
    #     ).scalar_one_or_none()
    #     if document is None:
    #         raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Document not found")
    #
    #     if document.sta
    #
    #     return True


def get_document_service(
    db_session: DBSessionDep, redis_client: RedisDep, s3_client: S3Dep
) -> DocumentService:
    return DocumentService(db_session, redis_client, s3_client)


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
