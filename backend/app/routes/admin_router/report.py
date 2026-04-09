from fastapi import APIRouter

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.schemas.report_schemas import (
    ReportedDocumentSchema,
    ReportHandleRequest,
    ReportSchema,
)
from app.services.auth_service import CurrentAdminDep
from app.services.report_service import ReportServiceDep

router = APIRouter(prefix="/reports")


@router.get("", response_model=ResponsePaginationSchema[ReportedDocumentSchema])
def get_reported_document(
    pagination: PaginationQueryDep,
    admin: CurrentAdminDep,
):
    return APIResponse.ok()


@router.get(
    "/documents/{document_id}", response_model=ResponsePaginationSchema[ReportSchema]
)
def list_pending_report_of_documents(
    document_id: int,
    pagination: PaginationQueryDep,
    admin: CurrentAdminDep,
    report_service: ReportServiceDep,
):
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
    admin: CurrentAdminDep,
    report_service: ReportServiceDep,
):
    report_service.handler_all_report_of_document(
        admin=admin,
        document_id=body.document_id,
        accept=body.accept,
        note=body.note,
    )
    return APIResponse.ok()
