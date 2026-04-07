from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.report_schemas import ReportReasonSchema, ReportRequest
from app.services.auth_service import CurrentUserDep, OptionalCurrentUserDep
from app.services.report_service import ReportServiceDep

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/available_reasons",
    response_model=ResponseSuccessSchema[list[ReportReasonSchema]],
)
def get_available_report_reasons(report_service: ReportServiceDep):
    data = report_service.get_available_reason()
    res_data = [ReportReasonSchema.model_validate(_) for _ in data]
    return APIResponse.ok(res_data)


@router.post("/documents/{document_id}", response_model=ResponseSuccessSchema)
def report_document(
    document_id: int,
    body: ReportRequest,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
):
    report_service.report_document(
        reporter_id=current_user.id,
        document_id=int(document_id),
        reason=body.reason,
        desc=body.desc,
    )
    return APIResponse.ok()
