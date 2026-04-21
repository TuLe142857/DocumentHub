from fastapi import APIRouter, Body, Query

from app.core import (
    APIResponse,
    ErrorCode,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
    build_error_docs,
)
from app.schemas.collection_schema import *
from app.schemas.document_schema import DocumentSummarySchema
from app.services.auth_service import CurrentUserDep
from app.services.collection_service import CollectionServiceDep
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post(
    "",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        (ErrorCode.RESOURCE_ALREADY_EXISTS, "Collection already exists."),
        ErrorCode.VALIDATION_ERROR,
    ),
)
def create_collection(
    current_user: CurrentUserDep,
    name: Annotated[str, Body(embed=True, alias="name")],
    collection_service: CollectionServiceDep,
):
    collection_service.create_collection(owner_id=current_user.id, name=name)
    return APIResponse.ok()


@router.get(
    "/{collection_id}/items",
    response_model=ResponsePaginationSchema[DocumentSummarySchema],
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        (ErrorCode.RESOURCE_NOT_FOUND, "Collection not found."),
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Get documents in collection",
)
def get_documents_in_collection(
    current_user: CurrentUserDep,
    collection_id: int,
    collection_service: CollectionServiceDep,
    storage_service: StorageServiceDep,
    query: Annotated[CollectionItemQuery, Query()],
):
    docs, total = collection_service.list_document(
        user=current_user,
        collection_id=int(collection_id),
        keyword=query.q,
        page=query.page,
        limit=query.limit,
    )
    res_data = [
        DocumentSummarySchema.build(doc, storage_service.generate_document_url(doc)[0])
        for doc in docs
    ]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res_data,
    )


@router.patch(
    "/{collection_id}",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        (ErrorCode.RESOURCE_NOT_FOUND, "Collection not found."),
        (ErrorCode.RESOURCE_ALREADY_EXISTS, "Collection name(new name) already exists"),
        (ErrorCode.FORBIDDEN, "User not have permission to update collection"),
        ErrorCode.VALIDATION_ERROR,
    ),
)
def rename_collection(
    current_user: CurrentUserDep,
    collection_id: int,
    new_name: Annotated[str, Body(embed=True)],
    collection_service: CollectionServiceDep,
):
    collection_service.rename_collection(
        user=current_user, collection_id=collection_id, new_name=new_name
    )
    return APIResponse.ok()


@router.delete(
    "/{collection_id}",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        (ErrorCode.RESOURCE_NOT_FOUND, "Collection not found."),
        (ErrorCode.FORBIDDEN, "User not have permission to delete collection"),
        ErrorCode.VALIDATION_ERROR,
    ),
)
def delete_collection(
    current_user: CurrentUserDep,
    collection_id: int,
    collection_service: CollectionServiceDep,
):
    collection_service.delete_collection(
        user=current_user,
        collection_id=collection_id,
    )
    return APIResponse.ok()


@router.put(
    "/{collection_id}/items/{document_id}",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        ErrorCode.RESOURCE_NOT_FOUND,
        ErrorCode.FORBIDDEN,
        ErrorCode.VALIDATION_ERROR,
    ),
)
def add_document_to_collection(
    current_user: CurrentUserDep,
    collection_id: int,
    document_id: int,
    collection_service: CollectionServiceDep,
):
    collection_service.add_document_to_collection(
        user=current_user,
        collection_id=collection_id,
        document_id=document_id,
    )
    return APIResponse.ok()


@router.delete(
    "/{collection_id}/items/{document_id}",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        ErrorCode.RESOURCE_NOT_FOUND,
        ErrorCode.FORBIDDEN,
        ErrorCode.VALIDATION_ERROR,
    ),
)
def remove_document_from_collection(
    current_user: CurrentUserDep,
    collection_id: int,
    document_id: int,
    collection_service: CollectionServiceDep,
):
    collection_service.remove_document_from_collection(
        user=current_user,
        collection_id=collection_id,
        document_id=document_id,
    )
    return APIResponse.ok()
