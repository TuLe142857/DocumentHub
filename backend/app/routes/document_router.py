from fastapi import APIRouter, Form

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.request.document_request import *
from app.schemas.response.document_response import *
from app.services.auth_service import AuthServiceDep
from app.services.document_service import DocumentServiceDep
from app.services.jwt_service import AccessToken, FreshAccessToken, OptionalAccessToken

router = APIRouter(prefix="/documents", tags=["Document"])


@router.get(
    "/supported_types",
    response_model=ResponseSuccessSchema[DocumentSupportedTypeResponse],
    summary="Get supported document types",
    description="Get supported document types",
)
def get_supported_types():
    res_data = DocumentSupportedTypeResponse(
        supported_type=get_settings().SUPPORTED_FILE_TYPE
    )
    return APIResponse.ok(data=res_data)


@router.get(
    "",
    response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]],
    summary="Get documents list of current user",
)
def get_document_list(
    access_token: AccessToken,
    document_service: DocumentServiceDep,
    auth_service: AuthServiceDep,
):
    owner_id = auth_service.get_user_id(access_token.__dict__())
    doc_seq = document_service.get_document_by_owner_id(owner_id)
    response_data = [DocumentSummaryResponse.model_validate(_) for _ in doc_seq]
    return APIResponse.ok(data=response_data)


@router.post("", response_model=ResponseSuccessSchema)
def upload_document(
    body: Annotated[DocumentUploadFormRequest, Form(media_type="multipart/form-data")],
    access_token: AccessToken,
    document_service: DocumentServiceDep,
    auth_service: AuthServiceDep,
):
    document_service.create_document(
        owner_id=auth_service.get_user_id(access_token.__dict__()),
        title=body.title,
        category_id=body.category_id,
        visibility=body.visibility,
        desc=body.desc,
        tags=body.tags,
        file=body.file.file,
        file_type=body.file_type,
        content_type=body.file.content_type,
    )
    return APIResponse.ok()


@router.get(
    "/{document_id}",
    response_model=ResponseSuccessSchema[DocumentDetailsResponse],
    summary="Get document details",
)
def get_document_details(
    access_token: OptionalAccessToken,
    document_id: int,
    document_service: DocumentServiceDep,
):
    # increase document view here
    if access_token:
        # user login
        pass
    else:
        # guest
        pass
    return APIResponse.ok()


@router.patch("/{document_id}", response_model=ResponseSuccessSchema)
def update_document(access_token: AccessToken, document_id: int):
    return APIResponse.ok()


@router.delete("/{document_id}", response_model=ResponseSuccessSchema)
def delete_document(access_token: FreshAccessToken, document_id: int):
    return APIResponse.ok()


@router.get(
    "/{document_id}/download",
    response_model=ResponseSuccessSchema,
    summary="Download document",
)
def download_document(access_token: OptionalAccessToken, document_id: int):
    # increase document download here
    if access_token:
        # user login
        pass
    else:
        # guest
        pass
    return APIResponse.ok()


@router.post(
    "/{document_id}/tags",
    response_model=ResponseSuccessSchema,
    summary="Add tag to document",
)
def add_tag(access_token: AccessToken, document_id: int, tags: list[str]):
    return APIResponse.ok()


@router.delete(
    "/{document_id}/tags",
    response_model=ResponseSuccessSchema,
    summary="Remove tag from document",
)
def remove_tag(access_token: AccessToken, document_id: int, tags: list[str]):
    return APIResponse.ok()


@router.post(
    "/{document_id}/like", response_model=ResponseSuccessSchema, summary="Like document"
)
def like_document(access_token: AccessToken, document_id: int):
    return APIResponse.ok()


@router.delete(
    "/{document_id}/like",
    response_model=ResponseSuccessSchema,
    summary="UnLike document",
)
def unlike_document(access_token: AccessToken, document_id: int):
    return APIResponse.ok()
