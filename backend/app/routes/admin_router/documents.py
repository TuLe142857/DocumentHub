from fastapi import APIRouter

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)

router = APIRouter(prefix="/documents")


@router.post("/{document_id}/unban", response_model=ResponseSuccessSchema)
def unban_document():
    return APIResponse.ok()
