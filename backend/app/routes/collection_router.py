from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.collection_schema import *
from app.schemas.document_schema import DocumentSummaryResponse
from app.services.collection_service import CollectionServiceDep
from app.services.jwt_service import AccessToken

router = APIRouter(prefix="/collections", tags=["Collection"])


@router.get("", response_model=ResponseSuccessSchema[list[CollectionSummaryResponse]])
def get_collection_list(
    access_token: AccessToken, collection_service: CollectionServiceDep
):
    collections = collection_service.list_collection(owner_id=int(access_token.sub))
    res = [CollectionSummaryResponse.model_validate(obj) for obj in collections]
    return APIResponse.ok(data=res)


@router.post("", response_model=ResponseSuccessSchema)
def create_collection(
    access_token: AccessToken,
    body: CollectionCreateRequest,
    collection_service: CollectionServiceDep,
):
    collection_service.create_collection(owner_id=int(access_token.sub), name=body.name)
    return APIResponse.ok()


@router.get(
    "/{collection_id}/items",
    response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]],
    summary="Get documents in collection",
)
def get_documents_in_collection(
    access_token: AccessToken,
    collection_id: int,
    collection_service: CollectionServiceDep,
):
    documents = collection_service.list_document(
        user_id=int(access_token.sub),
        collection_id=int(collection_id),
    )
    res = [DocumentSummaryResponse.model_validate(obj) for obj in documents]
    return APIResponse.ok(data=res)


@router.patch("/{collection_id}", response_model=ResponseSuccessSchema)
def rename_collection(
    access_token: AccessToken,
    collection_id: int,
    body: CollectionRenameRequest,
    collection_service: CollectionServiceDep,
):
    collection_service.rename_collection(
        user_id=int(access_token.sub), collection_id=collection_id, new_name=body.name
    )
    return APIResponse.ok()


@router.delete("/{collection_id}", response_model=ResponseSuccessSchema)
def delete_collection(
    access_token: AccessToken,
    collection_id: int,
    collection_service: CollectionServiceDep,
):
    collection_service.delete_collection(
        user_id=int(access_token.sub),
        collection_id=collection_id,
    )
    return APIResponse.ok()


@router.put(
    "/{collection_id}/items/{document_id}", response_model=ResponseSuccessSchema
)
def add_document_to_collection(
    access_token: AccessToken,
    collection_id: int,
    document_id: int,
    collection_service: CollectionServiceDep,
):
    collection_service.add_document_to_collection(
        user_id=int(access_token.sub),
        collection_id=collection_id,
        document_id=document_id,
    )
    return APIResponse.ok()


@router.delete(
    "/{collection_id}/items/{document_id}", response_model=ResponseSuccessSchema
)
def remove_document_from_collection(
    access_token: AccessToken,
    collection_id: int,
    document_id: int,
    collection_service: CollectionServiceDep,
):
    collection_service.remove_document_from_collection(
        user_id=int(access_token.sub),
        collection_id=collection_id,
        document_id=document_id,
    )
    return APIResponse.ok()
