from fastapi import APIRouter, Body
from typing import Annotated

from app.core import (
    APIResponse,
    AppException,
    ErrorCode,
    ResponseErrorSchema,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.core.sercurity import AccessToken
from app.services.auth_service import AuthServiceDep
from app.services.document_service import DocumentServiceDep

router = APIRouter(prefix="/categories")


@router.post("", response_model=ResponseSuccessSchema)
def create_category(
    category_name: Annotated[str, Body(alias="name", embed=True)],
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    document_service: DocumentServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN, "Access Denied")
    document_service.create_category(category_name)
    return APIResponse.ok()


@router.patch("/{category_id}", response_model=ResponseSuccessSchema)
def rename_category(
    category_id: int,
    category_new_name: Annotated[str , Body(alias="new_name", embed=True)],
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    document_service: DocumentServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN, "Access Denied")
    document_service.rename_category(category_id, category_new_name)
    return APIResponse.ok()


@router.delete(
    "/{category_id}",
    response_model=ResponseSuccessSchema,
    description="Delete category. Return error if category is used",
)
def delete_category(
    category_id: int,
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    document_service: DocumentServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN, "Access Denied")
    document_service.delete_category(category_id)
    return APIResponse.ok()
