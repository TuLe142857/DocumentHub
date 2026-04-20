from fastapi import APIRouter, Body, Form, Query

from app.core import (
    APIResponse,
    ResponseSuccessSchema,
)
from app.schemas.document_schema import *
from app.services.auth_service import (
    CurrentUserDep,
    OptionalCurrentUserDep,
)
from app.services.collection_service import CollectionServiceDep
from app.services.document_service import DocumentServiceDep
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get(
    "/supported_types",
    response_model=ResponseSuccessSchema[list[str]],
    summary="Get supported document types",
    description="Returns a list of supported document file types as extensions (e.g. '.pdf', '.docx').",
)
def get_supported_types():
    settings = get_settings()
    return APIResponse.ok(data=settings.SUPPORTED_FILE_TYPE)


@router.get(
    "/max_size",
    response_model=ResponseSuccessSchema[int],
    summary="Get max upload file size",
    description="Returns the maximum supported document upload size in bytes.",
)
def get_max_supported_document_size_bytes():
    settings = get_settings()
    return APIResponse.ok(data=settings.MAX_FILE_SIZE)


@router.post(
    "",
    response_model=ResponseSuccessSchema,
    summary="Upload document. Require login",
    description="Upload a new document.",
)
def upload_document(
    body: Annotated[DocumentUploadRequest, Form(media_type="multipart/form-data")],
    current_user: CurrentUserDep,
    document_service: DocumentServiceDep,
):
    document_service.create_document(
        owner_id=current_user.id,
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
    response_model=ResponseSuccessSchema[DocumentDetailsSchema],
    summary="Get document details",
    description="Retrieve detailed information of a specific document.",
)
def get_document_details(
    current_user: OptionalCurrentUserDep,
    document_id: int,
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    document = document_service.view_document(current_user, document_id)

    thumbnail_url, preview_url, _ = storage_service.generate_document_url(document)

    check_like = False
    if current_user is not None:
        check_like = document_service.check_like(document_id, current_user.id)

    response_data = DocumentDetailsSchema.build(
        document,
        thumbnail_url=thumbnail_url,
        preview_url=preview_url,
        liked=check_like,
    )

    return APIResponse.ok(data=response_data)


@router.patch(
    "/{document_id}",
    response_model=ResponseSuccessSchema[DocumentUpdateRequest],
    summary="Update document",
)
def update_document(
    document_service: DocumentServiceDep,
    current_user: CurrentUserDep,
    document_id: int,
    body: DocumentUpdateRequest,
):
    update_data = body.model_dump(exclude_unset=True)
    document_service.update_document(
        user=current_user, document_id=document_id, **update_data
    )
    return APIResponse.ok(data=update_data)


@router.delete(
    "/{document_id}",
    response_model=ResponseSuccessSchema,
    summary="Move document to trash",
    description="Soft delete a document. It can be restored before permanent deletion.",
)
def delete_document(
    document_service: DocumentServiceDep,
    current_user: CurrentUserDep,
    document_id: int,
):
    document_service.soft_delete_document(user=current_user, document_id=document_id)
    return APIResponse.ok()


@router.post(
    "/{document_id}/restore",
    response_model=ResponseSuccessSchema,
    summary="Restore document",
    description="Restore a document from the trash.",
)
def restore_document(
    document_service: DocumentServiceDep,
    current_user: CurrentUserDep,
    document_id: int,
):
    document_service.restore_document(user=current_user, document_id=document_id)
    return APIResponse.ok()


@router.put(
    "/{document_id}/tags",
    response_model=ResponseSuccessSchema,
    summary="Add tag to document",
)
def add_tag(
    current_user: CurrentUserDep,
    document_id: int,
    body: DocumentTagSchema,
    document_service: DocumentServiceDep,
):
    document_service.add_tag_to_document(
        user=current_user, document_id=document_id, tag_name=body.tag_name
    )
    return APIResponse.ok()


@router.delete(
    "/{document_id}/tags",
    response_model=ResponseSuccessSchema,
    summary="Remove tag from document",
)
def remove_tag(
    current_user: CurrentUserDep,
    document_id: int,
    body: DocumentTagSchema,
    document_service: DocumentServiceDep,
):
    document_service.remove_tag_from_document(
        user=current_user, document_id=document_id, tag_name=body.tag_name
    )
    return APIResponse.ok()


@router.put(
    "/{document_id}/like",
    response_model=ResponseSuccessSchema,
    summary="Like document",
    description="Mark a document as liked by the current user.",
)
def like_document(
    current_user: CurrentUserDep, document_id: int, document_service: DocumentServiceDep
):
    document_service.like_document(user=current_user, document_id=document_id)
    return APIResponse.ok()


@router.delete(
    "/{document_id}/like",
    response_model=ResponseSuccessSchema,
    summary="Unlike document",
    description="Remove like from a document.",
)
def unlike_document(
    current_user: CurrentUserDep, document_id: int, document_service: DocumentServiceDep
):
    document_service.unlike_document(user=current_user, document_id=document_id)
    return APIResponse.ok()


@router.get(
    "/{document_id}/download",
    response_model=ResponseSuccessSchema[str],
    summary="Download document",
    description="Download a document in the specified format. Response data is a url for download.",
)
def download_document(
    current_user: OptionalCurrentUserDep,
    document_id: int,
    document_service: DocumentServiceDep,
    document_type: Annotated[
        str, Query(description="Document format to download", alias="format")
    ] = ".pdf",
):
    url = document_service.download_document(
        user=current_user, document_id=document_id, document_format=document_type
    )
    return APIResponse.ok(data=url)


@router.put(
    "/{document_id}/collections",
    response_model=ResponseSuccessSchema,
    summary="Sync document collections",
    description=(
        "Synchronize the list of collections for a document."
        "This will add the document to new collections and remove "
        "it from any existing collections not included in the provided list. "
        "Operation is scoped to the current user's collections only."
    ),
)
def put_document_to_collections(
    collection_ids: Annotated[list[int], Body(embed=True)],
    document_id: int,
    current_user: CurrentUserDep,
    collection_service: CollectionServiceDep,
):
    collection_service.sync_document_collections(
        user=current_user, document_id=document_id, collection_ids=collection_ids
    )
    return APIResponse.ok(message="ok")
