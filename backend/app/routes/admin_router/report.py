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
    query: PaginationQueryDep,
    admin: CurrentAdminDep,
    report_service: ReportServiceDep,
):
    data, total = report_service.list_reported_documents(
        page=query.page, limit=query.limit
    )
    res = []
    for d in data:
        schema = ReportedDocumentSchema.model_validate(d[0])
        schema.report_count = d[1]
        res.append(schema)
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res,
    )


@router.get(
    "/documents/{document_id}", response_model=ResponsePaginationSchema[ReportSchema]
)
def list_pending_report_of_documents(
    document_id: int,
    query: PaginationQueryDep,
    admin: CurrentAdminDep,
    report_service: ReportServiceDep,
):
    reports, count = report_service.list_pending_reports(
        document_id=document_id, page=query.page, limit=query.limit
    )
    res_data = [ReportSchema.model_validate(_) for _ in reports]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=count,
        data=res_data,
    )


@router.post("/documents/{document_id}", response_model=ResponseSuccessSchema)
def handle_report(
    body: ReportHandleRequest,
    admin: CurrentAdminDep,
    document_id: int,
    report_service: ReportServiceDep,
):
    report_service.handler_all_report_of_document(
        admin=admin,
        document_id=document_id,
        accept=body.accept,
        note=body.note,
    )
    return APIResponse.ok()
