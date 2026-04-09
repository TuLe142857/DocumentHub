from fastapi import APIRouter, Body

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.schemas.collection_schema import *
from app.schemas.document_schema import DocumentSummaryResponse
from app.services.auth_service import CurrentUserDep
from app.services.collection_service import CollectionServiceDep

router = APIRouter(prefix="/collections", tags=["Collection"])


@router.get(
    "",
    response_model=ResponsePaginationSchema[str],
    summary="Get all collections of current user",
)
def get_collection_list(
    current_user: CurrentUserDep,
    pagination: PaginationQueryDep,
    collection_service: CollectionServiceDep,
):
    collections, total = collection_service.list_collection(
        owner_id=current_user.id,
        page=pagination.page,
        limit=pagination.limit,
    )
    res = [CollectionSummaryResponse.model_validate(obj) for obj in collections]
    return APIResponse.paginate(
        current_page=pagination.page,
        per_page=pagination.limit,
        total_items=total,
        data=res,
    )


@router.post("", response_model=ResponseSuccessSchema)
def create_collection(
    current_user: CurrentUserDep,
    name: Annotated[str, Body(embed=True, alias="name")],
    collection_service: CollectionServiceDep,
):
    collection_service.create_collection(owner_id=current_user.id, name=name)
    return APIResponse.ok()


@router.get(
    "/{collection_id}/items",
    response_model=ResponsePaginationSchema[DocumentSummaryResponse],
    summary="Get documents in collection",
)
def get_documents_in_collection(
    current_user: CurrentUserDep,
    collection_id: int,
    collection_service: CollectionServiceDep,
    pagination: PaginationQueryDep,
):
    documents, total = collection_service.list_document(
        user=current_user,
        collection_id=int(collection_id),
        page=pagination.page,
        limit=pagination.limit,
    )
    res = [DocumentSummaryResponse.model_validate(obj) for obj in documents]
    return APIResponse.paginate(
        current_page=pagination.page,
        per_page=pagination.limit,
        total_items=total,
        data=res,
    )


@router.patch("/{collection_id}", response_model=ResponseSuccessSchema)
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


@router.delete("/{collection_id}", response_model=ResponseSuccessSchema)
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
    "/{collection_id}/items/{document_id}", response_model=ResponseSuccessSchema
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
    "/{collection_id}/items/{document_id}", response_model=ResponseSuccessSchema
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
