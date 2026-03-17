from fastapi import APIRouter

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.schemas.document_schema import DocumentSummaryResponse
from app.services.jwt_service import AccessToken, OptionalAccessToken

router = APIRouter(prefix="/users", tags=["UserProfile"])


@router.get("/me/profile", response_model=ResponseSuccessSchema)
def get_self_profile(access_token: AccessToken):
    return APIResponse.ok()


@router.patch("/me/profile", response_model=ResponseSuccessSchema)
def update_self_profile(access_token: AccessToken):
    return APIResponse.ok()


@router.put("/me/avatar", response_model=ResponseSuccessSchema)
def update_avatar(
    access_token: AccessToken,
):
    return APIResponse.ok()


@router.get("/{username}/profile", response_model=ResponseSuccessSchema)
def get_userprofile(
    username: str,
    access_token: OptionalAccessToken,
):
    return APIResponse.ok()


@router.get(
    "/{username}/documents",
    response_model=ResponsePaginationSchema[DocumentSummaryResponse],
)
def get_user_documents(
    username: str,
    pagination: PaginationQueryDep,
    access_token: OptionalAccessToken,
):
    return APIResponse.paginate(
        current_page=pagination.page, per_page=pagination.limit, total_items=0, data=[]
    )
