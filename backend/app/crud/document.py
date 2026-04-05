import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.dependencies import DBSessionDep
from app.models import *

from .base import CRUDBase


class CRUDDocument(CRUDBase[Document, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(Document, db_session)

    def add_tags(
        self,
        document: Document,
        tags: list[str | Tag],
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> Document:
        for tag in tags:
            tag_obj = (
                tag if isinstance(tag, Tag) else Tag.get_or_create(tag, self.db_session)
            )
            if not tag_obj in document.tags:
                document.tags.append(tag_obj)
        return self._save(document, auto_commit=auto_commit, auto_flush=auto_flush)

    def remove_tags(
        self,
        document: Document,
        tags: list[str | Tag],
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> Document:

        tag_names_to_remove = {t if isinstance(t, str) else t.name for t in tags}
        document.tags = [t for t in document.tags if t.name not in tag_names_to_remove]

        return self._save(document, auto_commit=auto_commit, auto_flush=auto_flush)

    def add_like(
        self,
        document: Document,
        user_id: int,
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> Document:

        # check liked
        if self.db_session.execute(
            select(DocumentLike).where(
                and_(
                    DocumentLike.document_id == document.id,
                    DocumentLike.user_id == user_id,
                )
            )
        ).scalar_one_or_none():
            return document

        document.liked_by.append(DocumentLike(document_id=document.id, user_id=user_id))
        document.like_count += 1
        return self._save(document, auto_commit=auto_commit, auto_flush=auto_flush)

    def remove_like(
        self,
        document: Document,
        user_id: int,
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> Document:

        # check liked
        doc_like = self.db_session.execute(
            select(DocumentLike).where(
                and_(
                    DocumentLike.document_id == document.id,
                    DocumentLike.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if doc_like is not None:
            self.db_session.delete(doc_like)
            document.like_count -= 1
            return self._save(document, auto_commit=auto_commit, auto_flush=auto_flush)
        else:
            return document

    def ban(
        self, document: Document, *, auto_commit: bool = False, auto_flush: bool = True
    ) -> Document:
        document.banned_at = datetime.datetime.now(datetime.timezone.utc)
        document.status = DocumentStatus.BANNED

        return self._save(document, auto_commit=auto_commit, auto_flush=auto_flush)

    def soft_delete(
        self, document: Document, *, auto_commit: bool = False, auto_flush: bool = True
    ) -> Document:
        document.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        document.status = DocumentStatus.DELETED

        return self._save(document, auto_commit=auto_commit, auto_flush=auto_flush)

    def get_trash_list(self, user_id: int) -> list[Document]:
        pass

    def restore_document_from_trash(
        self, document: Document, *, auto_commit: bool = False, auto_flush: bool = True
    ) -> Document:
        pass


def get_crud_document(db_session: DBSessionDep) -> CRUDDocument:
    return CRUDDocument(db_session=db_session)


CRUDDocumentDep = Annotated[CRUDDocument, Depends(get_crud_document)]
