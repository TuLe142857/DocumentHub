from fastapi import APIRouter

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)

router = APIRouter(prefix="/reports")
from app.services.report_service import ReportServiceDep


@router.get("", response_model=ResponsePaginationSchema)
def get_reported_document_list(
    pagination: PaginationQueryDep,
):

    return APIResponse.ok()


@router.get("/documents/{document_id}", response_model=ResponseSuccessSchema)
def get_report_list_of_documents():
    return APIResponse.ok()


@router.post("/documents/{document_id}", response_model=ResponseSuccessSchema)
def handle_report():
    return APIResponse.ok()
