from fastapi import APIRouter

from app.core import (
    APIResponse,
    ResponseSuccessSchema,
)
from app.services.auth_service import CurrentAdminDep
from app.services.document_service import DocumentServiceDep

router = APIRouter(prefix="/documents")


@router.post("/{document_id}/unban", response_model=ResponseSuccessSchema)
def unban_document(
    document_id: int,
    admin: CurrentAdminDep,
    document_service: DocumentServiceDep,
):
    document_service.unban_document(admin_id=admin.id, document_id=document_id)
    return APIResponse.ok()
