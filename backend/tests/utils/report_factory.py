from app.models import *
from sqlalchemy.orm import Session

import random


class ReportFactory:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self, document: Document, reporter: User, reason: ReportReason
    ) -> DocumentReport:
        doc_report = DocumentReport(
            document=document, reporter=reporter, reason=reason, desc="..."
        )
        self.db_session.add(document)
        self.db_session.commit()
        return doc_report

    def create_many(
        self, document: Document, reporters: list[User], reasons: list[ReportReason]
    ) -> list[DocumentReport]:
        doc_reports = [
            DocumentReport(
                document=document,
                reporter=reporter,
                reason=random.choice(reasons),
                desc="...",
            )
            for reporter in reporters
        ]
        for doc_report in doc_reports:
            self.db_session.add(doc_report)
        self.db_session.commit()
        return doc_reports
