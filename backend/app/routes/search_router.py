from typing import Annotated

from fastapi import APIRouter, Query

from app.core import APIResponse, ResponsePaginationSchema
from app.schemas.document_schema import DocumentPublicQuery, DocumentSummarySchema
from app.services.document_service import DocumentServiceDep

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=ResponsePaginationSchema[DocumentSummarySchema])
def search(
    query: Annotated[DocumentPublicQuery, Query()], document_service: DocumentServiceDep
):
    docs, total_docs = document_service.get_public_documents(
        **query.model_dump(exclude_none=True)
    )
    res_data = [DocumentSummarySchema.model_validate(doc) for doc in docs]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total_docs,
        data=res_data,
    )
