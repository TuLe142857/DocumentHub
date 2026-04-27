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
from app.services.access_control_service import (
    AccessControlService,
    AccessControlServiceDep,
)


class ReportService:
    def __init__(
        self,
        db_session: Session,
        crud_user: CRUDUser,
        crud_doc: CRUDDocument,
        crud_report: CRUDReport,
        access_control: AccessControlService,
    ):
        self.db_session = db_session
        self.crud_user = crud_user
        self.crud_doc = crud_doc
        self.crud_report = crud_report
        self.access_control = access_control

    def get_available_reason(self) -> Sequence[ReportReason]:
        return self.db_session.execute(select(ReportReason)).scalars().all()

    def report_document(
        self, reporter: User, document_id: int, reason: int, desc: str | None
    ):
        document = self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )

        err = self.access_control.can_access_document(reporter, document)
        if err:
            raise err

        report_reason = self.db_session.execute(
            select(ReportReason).where(ReportReason.id == reason)
        ).scalar_one_or_none()
        if report_reason is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Invalid Report Reason")

        # check if user has report this document...
        report_in_db = self.db_session.execute(
            select(DocumentReport).where(
                DocumentReport.reporter_id == reporter.id,
                DocumentReport.document_id == document_id,
                DocumentReport.status == ReportStatus.PENDING,
            )
        ).scalar_one_or_none()

        if report_in_db is not None:
            raise AppException(
                ErrorCode.ACTION_ALREADY_PERFORMED,
                "You have already reported this document and it is still under review.",
            )

        # make report
        self.crud_report.create(
            DocumentReport(
                document=document, reporter=reporter, report_reason_id=reason, desc=desc
            )
        )

    def list_reported_documents(
        self, page: int, limit: int
    ) -> tuple[Sequence[tuple[Document, int]], int]:
        stmt = (
            select(Document, func.count(DocumentReport.id).label("report_count"))
            .join(DocumentReport)
            .where(DocumentReport.status == ReportStatus.PENDING)
            .group_by(Document.id)
        )

        count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )
        if count == 0:
            return [], 0

        rows = self.db_session.execute(
            stmt.offset((page - 1) * limit).limit(limit)
        ).all()

        res = [(r.Document, r.report_count) for r in rows]

        return res, count

    def list_pending_reports(
        self, document_id: int, page: int = 1, limit: int = 10
    ) -> tuple[Sequence[DocumentReport], int]:
        self.crud_doc.get(
            document_id,
            on_not_found=AppException(
                ErrorCode.RESOURCE_NOT_FOUND, "Document not found"
            ),
        )
        return self.crud_report.get_multi(
            DocumentReport.status == ReportStatus.PENDING,
            DocumentReport.document_id == document_id,
            skip=(page - 1) * limit,
            limit=limit,
        )

    def handler_all_report_of_document(
        self, admin: User, document_id: int, accept: bool, note: str | None
    ):
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

        effected_row_count = self.db_session.execute(
            update(DocumentReport)
            .where(
                DocumentReport.document_id == document_id,
                DocumentReport.status == ReportStatus.PENDING,
            )
            .values(status=ReportStatus.RESOLVED if accept else ReportStatus.REJECTED)
        ).rowcount

        if effected_row_count == 0:
            return

        mod_log = ModerationLog(
            admin_id=admin.id,
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
    access_control: AccessControlServiceDep,
) -> ReportService:
    return ReportService(db_session, crud_user, crud_doc, crud_report, access_control)


ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
