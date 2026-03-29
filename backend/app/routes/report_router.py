from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.core.sercurity.jwt import AccessToken
from app.schemas.report_schemas import ReportReasonResponse
from app.services.report_service import ReportServiceDep

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/available_reasons",
    response_model=ResponseSuccessSchema[list[ReportReasonResponse]],
)
def get_available_report_reasons(report_service: ReportServiceDep):
    data = report_service.get_available_reason()
    res_data = [ReportReasonResponse.model_validate(_) for _ in data]
    return APIResponse.ok(res_data)


@router.post("/documents/{document_id}", response_model=ResponseSuccessSchema)
def report_document(
    document_id: int,
    access_token: AccessToken,
):
    return APIResponse.ok()
