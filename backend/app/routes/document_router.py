from fastapi import APIRouter, Body, Form, Path, Query

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.core.sercurity import AccessToken, FreshAccessToken, OptionalAccessToken
from app.dependencies import DBSessionDep
from app.schemas.category_schema import CategorySchema
from app.schemas.document_schema import *
from app.services.auth_service import AuthServiceDep
from app.services.document_service import DocumentServiceDep
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/documents", tags=["Document"])


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


@router.get(
    "/categories",
    response_model=ResponseSuccessSchema[list[CategorySchema]],
    summary="List categories",
    description="Returns a list of all available document categories.",
)
def get_categories(document_service: DocumentServiceDep, db_session: DBSessionDep):
    from sqlalchemy import select

    from app.models import Category

    categories = db_session.execute(select(Category)).scalars().all()
    res = [CategorySchema.model_validate(category) for category in categories]
    return APIResponse.ok(data=res)


@router.get(
    "",
    response_model=ResponsePaginationSchema[DocumentSummaryResponse],
    summary="Get user documents. Require login.",
    description="Returns a paginated list of documents owned by the current user.",
)
def get_document_list(
    access_token: AccessToken,
    document_service: DocumentServiceDep,
    auth_service: AuthServiceDep,
    storage_service: StorageServiceDep,
    query: Annotated[DocumentQuery, Query()],
):
    owner_id = auth_service.get_user_id(access_token)

    doc_seq, total_items = document_service.list_self_documents(
        owner_id=owner_id, page=query.page, limit=query.limit, status=query.status
    )

    response_data = [
        DocumentSummaryResponse.from_object(
            _, storage_service.generate_presigned_url_for_document(_)[0]
        )
        for _ in doc_seq
    ]

    return APIResponse.paginate(
        data=response_data,
        current_page=query.page,
        per_page=query.limit,
        total_items=total_items,
    )


@router.post(
    "",
    response_model=ResponseSuccessSchema,
    summary="Upload document. Require login",
    description="Upload a new document.",
)
def upload_document(
    body: Annotated[DocumentUploadFormRequest, Form(media_type="multipart/form-data")],
    access_token: AccessToken,
    document_service: DocumentServiceDep,
    auth_service: AuthServiceDep,
):
    document_service.create_document(
        owner_id=auth_service.get_user_id(access_token),
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
    description="Retrieve detailed information of a specific document.",
)
def get_document_details(
    access_token: OptionalAccessToken,
    document_id: int,
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    user_id = int(access_token.sub) if (access_token is not None) else None

    document = document_service.view_document(user_id, document_id)

    response_data = DocumentDetailsResponse.from_object(
        document, *storage_service.generate_presigned_url_for_document(document)
    )

    # check document was liked by current user
    response_data.liked = document_service.is_liked(document_id, user_id)

    return APIResponse.ok(data=response_data)


@router.patch(
    "/{document_id}",
    response_model=ResponseSuccessSchema[DocumentUpdateRequest],
    summary="Update document",
)
def update_document(
    document_service: DocumentServiceDep,
    access_token: AccessToken,
    document_id: int,
    body: DocumentUpdateRequest,
):
    update_data = body.model_dump(exclude_unset=True)
    document_service.update_document(
        user_id=int(access_token.sub), document_id=document_id, **update_data
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
    access_token: FreshAccessToken,
    document_id: int,
):
    document_service.soft_delete_document(
        document_id=document_id, user_id=int(access_token.sub)
    )
    return APIResponse.ok()


@router.post(
    "/{document_id}/restore",
    response_model=ResponseSuccessSchema,
    summary="Restore document",
    description="Restore a document from the trash.",
)
def restore_document(
    document_service: DocumentServiceDep,
    access_token: AccessToken,
    document_id: int,
):
    document_service.restore_document(
        document_id=document_id, user_id=int(access_token.sub)
    )
    return APIResponse.ok()


@router.post(
    "/{document_id}/tags/{tag_name}",
    response_model=ResponseSuccessSchema,
    summary="Add tag to document",
)
def add_tag(
    access_token: AccessToken,
    document_id: int,
    tag_name: Annotated[str, Path()],
    document_service: DocumentServiceDep,
):
    document_service.add_tag_to_document(
        document_id=document_id, user_id=int(access_token.sub), tag_name=tag_name
    )
    return APIResponse.ok()


@router.delete(
    "/{document_id}/tags/{tag_name}",
    response_model=ResponseSuccessSchema,
    summary="Remove tag from document",
)
def remove_tag(
    access_token: AccessToken,
    document_id: int,
    tag_name: Annotated[str, Path()],
    document_service: DocumentServiceDep,
):
    document_service.remove_tag_from_document(
        document_id=document_id, user_id=int(access_token.sub), tag_name=tag_name
    )
    return APIResponse.ok()


@router.post(
    "/{document_id}/like",
    response_model=ResponseSuccessSchema,
    summary="Like document",
    description="Mark a document as liked by the current user.",
)
def like_document(
    access_token: AccessToken, document_id: int, document_service: DocumentServiceDep
):
    document_service.like_document(
        document_id=document_id, user_id=int(access_token.sub)
    )
    return APIResponse.ok()


@router.delete(
    "/{document_id}/like",
    response_model=ResponseSuccessSchema,
    summary="Unlike document",
    description="Remove like from a document.",
)
def unlike_document(
    access_token: AccessToken, document_id: int, document_service: DocumentServiceDep
):
    document_service.unlike_document(
        document_id=document_id, user_id=int(access_token.sub)
    )
    return APIResponse.ok()


@router.get(
    "/{document_id}/download",
    response_model=ResponseSuccessSchema[str],
    summary="Download document",
    description="Download a document in the specified format. Response data is a url for download.",
)
def download_document(
    access_token: OptionalAccessToken,
    document_id: int,
    document_service: DocumentServiceDep,
    document_type: Annotated[
        str, Query(description="Document format to download", alias="format")
    ] = ".pdf",
):
    user_id = int(access_token.sub) if access_token else None
    url = document_service.download_document(
        user_id=user_id, document_id=document_id, document_format=document_type
    )
    return APIResponse.ok(data=url)
