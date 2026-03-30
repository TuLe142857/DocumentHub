from fastapi import APIRouter

from app.core import (
    APIResponse,
    AppException,
    ErrorCode,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.core.sercurity import AccessToken
from app.services.auth_service import AuthServiceDep

router = APIRouter(prefix="/reports")
from app.schemas.report_schemas import (
    ReportedDocumentSchema,
    ReportHandleRequest,
    ReportSchema,
)
from app.services.report_service import ReportServiceDep


@router.get("", response_model=ResponsePaginationSchema[ReportedDocumentSchema])
def get_reported_document(
    pagination: PaginationQueryDep,
):

    return APIResponse.ok()


@router.get(
    "/documents/{document_id}", response_model=ResponsePaginationSchema[ReportSchema]
)
def list_pending_report_of_documents(
    document_id: int,
    pagination: PaginationQueryDep,
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    report_service: ReportServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN)
    reports, count = report_service.list_pending_reports(
        document_id=document_id, page=pagination.page, limit=pagination.limit
    )
    res_data = [ReportSchema.model_validate(_) for _ in reports]
    return APIResponse.paginate(
        current_page=pagination.page,
        per_page=pagination.limit,
        total_items=count,
        data=res_data,
    )


@router.post("/documents/{document_id}", response_model=ResponseSuccessSchema)
def handle_report(
    body: ReportHandleRequest,
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    report_service: ReportServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN)
    report_service.handler_all_report_of_document(
        document_id=body.document_id,
        admin_id=int(access_token.sub),
        accept=body.accept,
        note=body.note,
    )
    return APIResponse.ok()
