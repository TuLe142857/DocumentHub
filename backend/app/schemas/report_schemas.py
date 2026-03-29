from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ReportReasonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: Annotated[int, Field()]
    code: Annotated[str, Field()]


class ReportRequest(BaseModel):
    document_id: Annotated[int, Field()]
    reason: Annotated[int, Field(description="ReportReason.id")]
    desc: Annotated[str, Field(description="Report reason description")]
