from typing import Annotated

from fastapi import APIRouter, Body

from app.core import (
    APIResponse,
    ResponseSuccessSchema,
)
from app.services.auth_service import CurrentAdminDep
from app.services.category_service import CategoryServiceDep

router = APIRouter(prefix="/categories")


@router.post("", response_model=ResponseSuccessSchema)
def create_category(
    category_name: Annotated[str, Body(alias="name", embed=True)],
    admin: CurrentAdminDep,
    category_service: CategoryServiceDep,
):
    category_service.create_category(category_name)
    return APIResponse.ok()


@router.patch("/{category_id}", response_model=ResponseSuccessSchema)
def rename_category(
    category_id: int,
    category_new_name: Annotated[str, Body(alias="new_name", embed=True)],
    admin: CurrentAdminDep,
    category_service: CategoryServiceDep,
):
    category_service.rename_category(category_id, category_new_name)
    return APIResponse.ok()


@router.delete(
    "/{category_id}",
    response_model=ResponseSuccessSchema,
    description="Delete category. Return error if category is used",
)
def delete_category(
    category_id: int,
    admin: CurrentAdminDep,
    category_service: CategoryServiceDep,
):
    category_service.delete_category(category_id)
    return APIResponse.ok()
