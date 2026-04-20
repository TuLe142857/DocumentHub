from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep
from app.models import *
from app.models.document import document_tags_table


class SearchService:
    def __init__(
        self, db_session: Session, crud_doc: CRUDDocument, crud_user: CRUDUser
    ):
        self.db_session = db_session
        self.crud_doc = crud_doc
        self.crud_user = crud_user

    def search_documents(
        self,
        keyword: str | None = None,
        category_id: int | None = None,
        tags: Sequence[str] = None,
        page=1,
        limit: int = 20,
    ) -> tuple[Sequence[Document], int]:
        """
        Coming soon :)
        Returns: tuple[list, max count]
        """
        stmt = select(Document).where(
            Document.visibility == DocumentVisibility.PUBLIC,
            Document.status == DocumentStatus.READY,
        )

        keywords = keyword.strip() if keyword else None
        if keywords is not None and len(keywords) > 0:
            stmt = stmt.where(Document.title.like(f"%{keywords}%"))

        if category_id:
            stmt = stmt.where(Document.category_id == category_id)
        if tags:
            stmt = (
                stmt.join(
                    document_tags_table,
                    Document.id == document_tags_table.c.document_id,
                )
                .join(Tag, Tag.id == document_tags_table.c.tag_id)
                .where(Tag.name.in_(tags))
                .distinct()
            )

        total_count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )

        if total_count == 0:
            return [], 0

        res = (
            self.db_session.execute(stmt.offset((page - 1) * limit).limit(limit))
            .scalars()
            .all()
        )
        return res, total_count


def get_search_service(
    db_session: DBSessionDep, crud_doc: CRUDDocumentDep, crud_user: CRUDUserDep
) -> SearchService:
    return SearchService(db_session, crud_doc, crud_user)


SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
