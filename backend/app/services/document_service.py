import datetime
from typing import Annotated, BinaryIO, Sequence
import uuid

from fastapi import Depends
from mypy_boto3_s3 import S3Client
from redis import Redis
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode, get_settings
from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep, RedisDep, S3Dep
from app.models import *
from app.models.document import document_tags_table
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

    SORT_FIELD_MAP = {
        "title": Document.title,
        "view": Document.view_count,
        "like": Document.like_count,
        "download": Document.download_count,
        "created_at": Document.created_at,
    }

    def _parse_sort(self, s: str, raise_on_validate: bool = True):
        options = [_.strip() for _ in s.split(",")]
        sort_clauses = []
        for option in options:
            if not option:
                continue

            if option.startswith("-"):
                field = option[1:]
                direction = "desc"
            elif option.startswith("+"):
                field = option[1:]
                direction = "asc"
            else:
                field = option
                direction = "asc"  # default sort asc

            column = self.SORT_FIELD_MAP.get(field)
            if not column:
                if raise_on_validate:
                    msg = (
                        f"Invalid sort option '{option}' in '{s}'. "
                        f"Available options: {[key for key in self.SORT_FIELD_MAP]}. "
                        "Use '-' prefix for descending or '+' for ascending."
                        "Use ',' as separator between multi sort options."
                    )
                    raise AppException(ErrorCode.VALIDATION_ERROR, msg)
                else:
                    continue
            sort_clauses.append(column.desc() if direction == "desc" else column.asc())
        return sort_clauses

    def _apply_filter(
        self,
        stmt,
        q: str | None = None,
        types: list[str] | None = None,
        category_ids: list[int] | None = None,
        tags: list[str] | None = None,
        sort: str | None = None,
    ):
        if q is not None:
            stmt = stmt.where(Document.title.ilike(f"%{q.strip()}%"))
        if (types is not None) and (len(types) > 0):
            stmt = stmt.where(Document.file_type.in_(types))
        if (category_ids is not None) and (len(category_ids) > 0):
            stmt = stmt.where(Document.category_id.in_(category_ids))
        if (tags is not None) and (len(tags) > 0):
            stmt = (
                stmt.join(
                    document_tags_table,
                    Document.id == document_tags_table.c.document_id,
                )
                .join(Tag, Tag.id == document_tags_table.c.tag_id)
                .where(Tag.name.in_(tags))
                .distinct()
            )
        if (sort is not None) and (len(sort) > 0):
            sort_clauses = self._parse_sort(sort)
            if sort_clauses:
                stmt = stmt.order_by(*sort_clauses)
        else:
            stmt = stmt.order_by(Document.created_at.desc())
        return stmt

    def get_public_documents(
        self,
        owner_name: str | None = None,
        q: str | None = None,
        types: list[str] | None = None,
        category_ids: list[int] | None = None,
        tags: list[str] | None = None,
        sort: str | None = None,
        page=1,
        limit: int = 20,
    ) -> tuple[Sequence[Document], int]:
        """
        Select Public Documents.
        Any filter field with default value None will be ignored.
        Args:
            owner_name: owner.username
            q: query keyword
            types:
            category_ids:
            tags:
            sort:
            page:
            limit:

        Returns:

        Raises:
            AppException:
                - ErrorCode.RESOURCE_NOT_FOUND: if owner_name was provided but not exist in database.
        """

        # build base query statement
        stmt = select(Document).where(
            Document.visibility == DocumentVisibility.PUBLIC,
            Document.status == DocumentStatus.READY,
        )

        if owner_name is not None:
            owner = self.crud_user.get_by_identity(
                owner_name,
                on_not_found=AppException(
                    ErrorCode.RESOURCE_NOT_FOUND, "User not found"
                ),
            )
            stmt = stmt.where(Document.owner_id == owner.id)

        stmt = self._apply_filter(
            stmt,
            q=q,
            types=types,
            category_ids=category_ids,
            tags=tags,
            sort=sort,
        )

        # count
        total = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )
        if total == 0:
            return list(), 0

        # pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        res = self.db_session.execute(stmt).scalars().all()

        return res, total

    def get_my_documents(
        self,
        user_id: int,
        q: str | None = None,
        types: list[str] | None = None,
        category_ids: list[int] | None = None,
        tags: list[str] | None = None,
        sort: str | None = None,
        page=1,
        limit: int = 20,
        visibility: DocumentVisibility | None = None,
        statuses: list[DocumentStatus] | None = None,
    ) -> tuple[Sequence[Document], int]:
        """

        Args:
            user_id:
            q:
            types:
            category_ids:
            tags:
            sort:
            page:
            limit:
            visibility:
            statuses:

        Returns:

        """

        # check user exist
        self.crud_user.get(
            user_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )

        # build base query statement
        stmt = select(Document).where(
            Document.owner_id == user_id,
        )
        if visibility is not None:
            stmt = stmt.where(Document.visibility == visibility)
        if (statuses is not None) and (len(statuses) > 0):
            stmt = stmt.where(Document.status.in_(statuses))
        stmt = self._apply_filter(
            stmt,
            q=q,
            types=types,
            category_ids=category_ids,
            tags=tags,
            sort=sort,
        )

        # count
        total = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )
        if total == 0:
            return list(), 0

        # pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        res = self.db_session.execute(stmt).scalars().all()

        return res, total

    def get_documents_by_admin(
        self,
        q: str | None = None,
        owner_name: str | None = None,
        category_id: int = None,
        status: DocumentStatus | None = None,
        visibility: DocumentVisibility | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[Sequence[Document], int]:
        stmt = select(Document)
        stmt = self._apply_filter(stmt, q=q)

        if owner_name:
            stmt = stmt.join(User, User.id == Document.owner_id).where(
                User.username == owner_name
            )
        if status is not None:
            stmt = stmt.where(Document.status == status)
        if visibility is not None:
            stmt = stmt.where(Document.visibility == visibility)
        if category_id:
            stmt = stmt.where(Document.category_id == category_id)

        count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )
        if count == 0:
            return list(), 0

        stmt = stmt.offset((page - 1) * limit).limit(limit)

        res = self.db_session.execute(stmt).scalars().all()
        return res, count

    def get_liked_document(
        self, user_id: int, page: int = 0, limit: int = 10
    ) -> tuple[Sequence[Document], int]:
        stmt = (
            select(Document)
            .join(DocumentLike, DocumentLike.document_id == Document.id)
            .where(DocumentLike.user_id == user_id)
            .where(
                or_(
                    Document.owner_id == user_id,
                    and_(
                        Document.status == DocumentStatus.READY,
                        Document.visibility == DocumentVisibility.PUBLIC,
                    ),
                )
            )
        )
        total = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )
        if total == 0:
            return list(), 0
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        res = self.db_session.execute(stmt).scalars().all()
        return res, total

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
        """

        Args:
            owner_id:
            title:
            category_id:
            visibility:
            desc:
            tags:
            file:
            file_type:
            content_type:

        Returns:

        Raises:
            ErrorCode.RESOURCE_ALREADY_EXISTS:
            ErrorCode.RESOURCE_NOT_FOUND: category not found
        """

        # check title
        if (
            self.db_session.execute(
                select(Document).where(
                    Document.owner_id == owner_id, Document.title == title
                )
            ).scalar_one_or_none()
            is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Document already exists"
            )

        # check category
        if (
            self.db_session.execute(
                select(Category).where(Category.id == category_id)
            ).scalar_one_or_none()
            is None
        ):
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category not found")

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

    def view_document(self, user: User | None, document_id: int) -> Document:
        """
        If user is admin, return document, not increase view,
        else check permission and return document,
        increase document view.
        Args:
            user: viewer
            document_id: document.id

        Returns:

        Raises:
            ErrorCode.RESOURCE_NOT_FOUND:
            ErrorCode.RESOURCE_NOT_AVAILABLE:
            ErrorCode.FORBIDDEN
        """

        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        if user is None:
            # document view by guest (not login)
            err = self.access_control.can_access_by_anyone(document)
            if err:
                raise err
        else:
            if user.role.name == "ADMIN":
                return document
            # document view by user
            err = self.access_control.can_access_document(user, document)
            if err:
                raise err
            # increase view
            redis_view_key = f"view:doc:{document_id}:user:{user.id}"
            if self.redis_client.set(redis_view_key, "1", ex=3600, nx=True):
                document.view_count += 1
                self.db_session.flush()
        return document

    def download_document(
        self, user: User | None, document_id: int, document_format: str = ".pdf"
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

        err = (
            self.access_control.can_access_document(user, document)
            if user is not None
            else self.access_control.can_access_by_anyone(document)
        )
        if err:
            raise err

        available_formats = {".pdf", document.file_type}
        if document_format not in available_formats:
            raise AppException(
                ErrorCode.UNSUPPORTED_FILE_TYPE,
                f"Invalid document format for download. Available formats: {available_formats}",
            )

        if user is not None:
            redis_download_key = f"download:doc:{document_id}:user:{user.id}"
            if self.redis_client.set(redis_download_key, "1", ex=3600, nx=True):
                document.download_count += 1

        ori_url, pdf_url = self.storage_service.generate_download_url(document)

        if document_format == ".pdf":
            return pdf_url
        return ori_url

    def check_like(self, document_id: int, user_id: int):
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
        user: User,
        document_id: int,
        desc: str | None = None,
        title: str | None = None,
        category_id: int | None = None,
        visibility: DocumentVisibility | None = None,
        tags: list[str] | None = None,
    ):
        """

        Args:
            user:
            document_id:
            desc:
            title:
            category_id:
            visibility:
            tags:

        Returns:

        Raises:
            AppException: with the following ErrorCode

                - ErrorCode.RESOURCE_NOT_FOUND:
                - ErrorCode.FORBIDDEN:

        """
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_update_document(user, document)
        if err:
            raise err

        update_dict = {}
        if desc:
            update_dict["desc"] = desc
        if title:
            if self.db_session.execute(select(Document).where(
                Document.owner_id == document.owner_id,
                Document.title == title,
                Document.id != document_id,
            )).scalar_one_or_none() is not None:
                raise AppException(ErrorCode.RESOURCE_ALREADY_EXISTS, "Document title already exists")
            update_dict["title"] = title
        if category_id:
            if self.db_session.execute(select(Category).where(Category.id == category_id)).scalar_one_or_none() is None:
                raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category not found")
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

    def add_tag_to_document(self, user: User, document_id: int, tag_name: str):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_update_document(user, document)
        if err:
            raise err

        self.crud_doc.add_tags(document, [tag_name])

    def remove_tag_from_document(self, user: User, document_id: int, tag_name: str):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_update_document(user, document)
        if err:
            raise err

        self.crud_doc.remove_tags(self.crud_doc.get(document_id), [tag_name])

    def like_document(self, user: User, document_id: int):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_access_document(user, document)
        if err:
            raise err
        self.crud_doc.add_like(self.crud_doc.get(document_id), user.id)

    def unlike_document(self, user: User, document_id: int):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_access_document(user, document)
        if err:
            raise err

        self.crud_doc.remove_like(document, user.id)

    def soft_delete_document(self, user: User, document_id: int):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_delete_document(user, document)
        if err:
            raise err

        self.crud_doc.soft_delete(document)

    def restore_document(self, user: User, document_id: int):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_restore_document(user, document)
        if err:
            raise err

        if document.deleted_at is None:
            raise AppException(ErrorCode.RESOURCE_CONFLICT, "Document is not deleted")
        document.deleted_at = None
        if document.banned_at is not None:
            document.status = DocumentStatus.BANNED
        else:
            document.status = DocumentStatus.READY
        self.db_session.add(document)

    def ban_document(self, admin: User, document_id: int, note: str | None = None):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_ban_document(admin, document)
        if err:
            raise err

        if document.status == DocumentStatus.BANNED:
            raise AppException(
                ErrorCode.RESOURCE_CONFLICT, "Document is already banned"
            )

        document.status = DocumentStatus.BANNED
        document.banned_at = datetime.datetime.now(datetime.timezone.utc)
        moderation_log = ModerationLog(
            document_id=document_id,
            admin_id=admin.id,
            action=ModerationAction.BAN_DOCUMENT,
            note=note,
        )

        self.db_session.add(document)
        self.db_session.add(moderation_log)

    def unban_document(self, admin: User, document_id: int, note: str | None = None):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_unban_document(admin, document)
        if err:
            raise err

        if document.status != DocumentStatus.BANNED:
            raise AppException(ErrorCode.RESOURCE_CONFLICT, "Document not banned")

        if document.deleted_at is None:
            document.status = DocumentStatus.READY
        else:
            document.status = DocumentStatus.DELETED

        document.banned_at = None
        moderation_log = ModerationLog(
            document_id=document_id,
            admin_id=admin.id,
            action=ModerationAction.UNBAN_DOCUMENT,
            note=note,
        )

        self.db_session.add(document)
        self.db_session.add(moderation_log)

    def create_category(self, name: str):
        """
        Raises:
            AppException(ErrorCode.RESOURCE_ALREADY_EXISTS)
        """
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
        """

        Raises:
            AppException(ErrorCode.RESOURCE_NOT_FOUND)
            AppException(ErrorCode.RESOURCE_ALREADY_EXISTS)

        """
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
        """
        Raises:
            AppException(ErrorCode.RESOURCE_NOT_FOUND)
            AppException(ErrorCode.RESOURCE_IN_USE)
        """
        category = self.db_session.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()

        if category is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category does not exist")

        is_used = self.db_session.execute(
            select(Document).where(Document.category_id == category_id).limit(1)
        ).scalar_one_or_none()

        if is_used:
            raise AppException(ErrorCode.RESOURCE_IN_USE, "Category is in use")

        self.db_session.delete(category)


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
