from typing import Annotated

from fastapi import APIRouter, Query

from app.core import (
    APIResponse,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.schemas.document_schema import (
    DocumentAdminQuery,
    DocumentDetailsSchema,
    DocumentSummarySchema,
)
from app.services.auth_service import CurrentAdminDep
from app.services.document_service import DocumentServiceDep
from app.services.report_service import ReportServiceDep
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/documents")


@router.get("", response_model=ResponsePaginationSchema[DocumentSummarySchema])
def get_documents(
    query: Annotated[DocumentAdminQuery, Query()],
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
    admin: CurrentAdminDep,
):
    docs, total = document_service.get_documents_by_admin(
        q=query.q,
        owner_name=query.owner,
        category_id=query.category_id,
        visibility=query.visibility,
        status=query.status,
        page=query.page,
        limit=query.limit,
    )

    res = [
        DocumentSummarySchema.build(doc, storage_service.generate_document_url(doc)[0])
        for doc in docs
    ]
    return APIResponse.paginate(
        current_page=query.page, per_page=query.limit, total_items=total, data=res
    )


@router.get(
    "/{document_id}", response_model=ResponseSuccessSchema[DocumentDetailsSchema]
)
def get_document_details(
    admin: CurrentAdminDep,
    document_id: int,
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    doc = document_service.view_document(admin, document_id)
    res = DocumentDetailsSchema.build(
        doc, *storage_service.generate_document_url(doc)[0:2]
    )
    return APIResponse.ok(data=res)


@router.post("/{document_id}/unban", response_model=ResponseSuccessSchema)
def unban_document(
    document_id: int,
    admin: CurrentAdminDep,
    report_service: ReportServiceDep,
):
    report_service.unban_document(admin=admin, document_id=document_id)
    return APIResponse.ok()
