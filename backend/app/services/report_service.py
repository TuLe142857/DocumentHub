import datetime
from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.crud.document import CRUDDocument, CRUDDocumentDep
from app.crud.report import CRUDReport, CRUDReportDep
from app.crud.user import CRUDUser, CRUDUserDep
from app.dependencies import DBSessionDep
from app.models import *


class ReportService:
    def __init__(
        self,
        db_session: Session,
        crud_user: CRUDUser,
        crud_doc: CRUDDocument,
        crud_report: CRUDReport,
    ):
        self.db_session = db_session
        self.crud_user = crud_user
        self.crud_doc = crud_doc
        self.crud_report = crud_report

    def get_available_reason(self) -> Sequence[ReportReason]:
        return self.db_session.execute(select(ReportReason)).scalars().all()

    def report_document(
        self, reporter_id: int, document_id: int, reason: int, desc: str | None
    ):
        # check if user has report this document...
        report_in_db = self.db_session.execute(
            select(DocumentReport).where(
                DocumentReport.reporter_id == reporter_id,
                DocumentReport.document_id == document_id,
                DocumentReport.status == ReportStatus.PENDING,
            )
        ).scalar_one_or_none()
        if report_in_db is not None:
            raise AppException(
                ErrorCode.ACTION_ALREADY_PERFORMED,
                "You have already reported this document and it is still under review.",
            )

        reporter = self.crud_user.get(
            reporter_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        self.crud_report.create(
            DocumentReport(
                document=document, reporter=reporter, report_reason_id=reason, desc=desc
            )
        )

    def list_reported_documents(
        self, page: int, limit: int
    ) -> tuple[Sequence[Document], int]:
        stmt = (
            select(Document)
            .join(DocumentReport)
            .where(DocumentReport.status == ReportStatus.PENDING)
            .distinct()
        )

        count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalars()
            or 0
        )
        if count == 0:
            return [], 0

        res = (
            self.db_session.execute(stmt.offset((page - 1) * limit).limit(limit))
            .scalars()
            .all()
        )

        return res, count

    def list_pending_reports(
        self, document_id: int, page: int = 1, limit: int = 10
    ) -> tuple[Sequence[DocumentReport], int]:
        return self.crud_report.get_multi(
            DocumentReport.status == ReportStatus.PENDING,
            DocumentReport.document_id == document_id,
            skip=(page - 1) * limit,
            limit=limit,
        )

    def handler_all_report_of_document(
        self, document_id: int, admin_id: int, accept: bool, note: str | None
    ):
        admin: User = self.crud_user.get(
            admin_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )
        if admin.role.name != "ADMIN":
            raise AppException(ErrorCode.FORBIDDEN)

        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        if accept:
            document.banned_at = datetime.datetime.now(datetime.timezone.utc)
            document.status = DocumentStatus.BANNED

        self.db_session.execute(
            update(DocumentReport)
            .where(
                DocumentReport.document_id == document_id,
                DocumentReport.status == ReportStatus.PENDING,
            )
            .values(status=ReportStatus.RESOLVED if accept else ReportStatus.REJECTED)
        )

        mod_log = ModerationLog(
            admin_id=admin_id,
            document_id=document_id,
            action=ModerationAction.BAN_DOCUMENT
            if accept
            else ModerationAction.REJECT_REPORT,
            note=note,
        )

        self.db_session.add(mod_log)


def get_report_service(
    db_session: DBSessionDep,
    crud_user: CRUDUserDep,
    crud_doc: CRUDDocumentDep,
    crud_report: CRUDReportDep,
) -> ReportService:
    return ReportService(db_session, crud_user, crud_doc, crud_report)


ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
