import datetime
from typing import Annotated

from pydantic import AliasPath, BaseModel, ConfigDict, Field

from app.models import *

from .document_schema import DocumentSummarySchema


class ReportReasonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: Annotated[int, Field()]
    code: Annotated[str, Field()]


class ReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: Annotated[int, Field()]
    reporter_id: Annotated[int, Field()]
    document_id: Annotated[int, Field()]
    report_reason: Annotated[str, Field(validation_alias=AliasPath("reason", "code"))]
    desc: Annotated[str | None, Field()]
    status: Annotated[ReportStatus, Field]
    created_at: Annotated[datetime.datetime, Field()]


class ReportedDocumentSchema(DocumentSummarySchema):
    @staticmethod
    def count_report(doc: Document) -> int:
        r = [_ for _ in doc.reports if _.status == ReportStatus.PENDING]
        return len(r)

    report_count: Annotated[int, Field(default=0)]


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: Annotated[int, Field(description="ReportReason.id")]
    desc: Annotated[str, Field(default="", description="Report reason description")]


class ReportHandleRequest(BaseModel):
    note: Annotated[str | None, Field(default=None)]
    accept: Annotated[bool, Field(description="Accept report and ban document or not")]
