import datetime
import enum
from typing import Annotated, Any

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ORMBase


class ReportStatus(enum.Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ModerationAction(enum.Enum):
    REJECT_REPORT = "REJECT_REPORT"
    BAN_DOCUMENT = "BAN_DOCUMENT"
    UNBAN_DOCUMENT = "UNBAN_DOCUMENT"


class ReportReason(ORMBase):
    __tablename__ = "report_reasons"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class DocumentReport(ORMBase):
    __tablename__ = "document_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    report_reason_id: Mapped[int] = mapped_column(ForeignKey("report_reasons.id"))
    desc: Mapped[str | None] = mapped_column(Text)

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), server_default=ReportStatus.PENDING.value
    )
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )

    reporter: Mapped["User"] = relationship()
    report_reason: Mapped["ReportReason"] = relationship()
    document: Mapped["Document"] = relationship(back_populates="reports")
    reason: Mapped["ReportReason"] = relationship()


class ModerationLog(ORMBase):
    __tablename__ = "moderation_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[ModerationAction] = mapped_column(Enum(ModerationAction))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    # relationship ...

    admin: Mapped["User"] = relationship()
    document: Mapped["Document"] = relationship()
