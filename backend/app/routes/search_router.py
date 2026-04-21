from typing import Annotated

from fastapi import APIRouter, Query

from app.core import APIResponse, ErrorCode, ResponsePaginationSchema, build_error_docs
from app.schemas.document_schema import DocumentPublicQuery, DocumentSummarySchema
from app.services.document_service import DocumentServiceDep
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    response_model=ResponsePaginationSchema[DocumentSummarySchema],
    responses=build_error_docs(ErrorCode.VALIDATION_ERROR),
)
def search(
    query: Annotated[DocumentPublicQuery, Query()],
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    docs, total_docs = document_service.get_public_documents(
        **query.model_dump(exclude_none=True)
    )
    res_data = [
        DocumentSummarySchema.build(doc, storage_service.generate_document_url(doc)[0])
        for doc in docs
    ]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total_docs,
        data=res_data,
    )
