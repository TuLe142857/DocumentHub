from typing import Annotated, Literal, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep
from app.models import *


class RecommendationService:
    def __init__(
        self, db_session: Session, crud_doc: CRUDDocument, crud_user: CRUDUser
    ):
        self.db_session = db_session
        self.crud_doc = crud_doc
        self.crud_user = crud_user

    def get_personalize(self, user: User, limit: int) -> Sequence[Document]:
        """
        Coming soon :D
        """
        return (
            self.db_session.execute(
                select(Document)
                .where(
                    Document.visibility == DocumentVisibility.PUBLIC,
                )
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def get_trending(
        self,
        category_id,
        timeframe: Literal["daily", "weekly", "monthly", "all_time"],
        limit: int = 10,
    ) -> Sequence[Document]:
        """
        Coming soon :D
        """
        return (
            self.db_session.execute(
                select(Document)
                .where(
                    Document.category_id == category_id,
                    Document.visibility == DocumentVisibility.PUBLIC,
                )
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def get_similar(self, document_id: int, limit: int = 10) -> Sequence[Document]:
        """
        Coming soon :D
        """
        return (
            self.db_session.execute(
                select(Document)
                .where(
                    Document.visibility == DocumentVisibility.PUBLIC,
                )
                .limit(limit)
            )
            .scalars()
            .all()
        )


def get_recommendation_service(
    db_session: DBSessionDep,
    crud_doc: CRUDDocumentDep,
    crud_user: CRUDUserDep,
) -> RecommendationService:
    return RecommendationService(db_session, crud_doc, crud_user)


RecommendationServiceDep = Annotated[
    RecommendationService, Depends(get_recommendation_service)
]
