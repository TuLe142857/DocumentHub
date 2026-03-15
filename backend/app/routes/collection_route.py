from typing import Annotated

from fastapi import APIRouter, Body

from app.core import APIResponse, ResponseSuccessSchema
from app.dependencies import AccessTokenDep

router = APIRouter(prefix="/collections", tags=["Collection"])


@router.get("", response_model=ResponseSuccessSchema)
def get_collection_list(access_token: AccessTokenDep):
    return APIResponse.ok()


@router.get("/{collection_id}", response_model=ResponseSuccessSchema)
def get_collection_details(access_token: AccessTokenDep, collection_id: int):
    return APIResponse.ok()


@router.patch("/{collection_id}", response_model=ResponseSuccessSchema)
def rename_collection(access_token: AccessTokenDep, collection_id: int):
    return APIResponse.ok()


@router.delete("/{collection_id}", response_model=ResponseSuccessSchema)
def delete_collection(access_token: AccessTokenDep, collection_id: int):
    return APIResponse.ok()


@router.post("", response_model=ResponseSuccessSchema)
def create_collection(
    access_token: AccessTokenDep,
    collection_name: Annotated[str, Body(alias="collection_name")],
):
    return APIResponse.ok()


@router.put("/{collection_id}/items", response_model=ResponseSuccessSchema)
def add_document_to_collection(access_token: AccessTokenDep, collection_id: int):
    return APIResponse.ok()


@router.delete(
    "/{collection_id}/items/{document_id}", response_model=ResponseSuccessSchema
)
def remove_document_from_collection(
    access_token: AccessTokenDep, collection_id: int, document_id: int
):
    return APIResponse.ok()
