from typing import Annotated

from fastapi import APIRouter, Body

from app.core import (
    APIResponse,
    ResponseErrorSchema,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.services.auth_service import CurrentAdminDep
from app.services.document_service import DocumentServiceDep

router = APIRouter(prefix="/categories")


@router.post("", response_model=ResponseSuccessSchema)
def create_category(
    category_name: Annotated[str, Body(alias="name", embed=True)],
    admin: CurrentAdminDep,
    document_service: DocumentServiceDep,
):
    document_service.create_category(category_name)
    return APIResponse.ok()


@router.patch("/{category_id}", response_model=ResponseSuccessSchema)
def rename_category(
    category_id: int,
    category_new_name: Annotated[str, Body(alias="new_name", embed=True)],
    admin: CurrentAdminDep,
    document_service: DocumentServiceDep,
):
    document_service.rename_category(category_id, category_new_name)
    return APIResponse.ok()


@router.delete(
    "/{category_id}",
    response_model=ResponseSuccessSchema,
    description="Delete category. Return error if category is used",
)
def delete_category(
    category_id: int,
    admin: CurrentAdminDep,
    document_service: DocumentServiceDep,
):
    document_service.delete_category(category_id)
    return APIResponse.ok()
