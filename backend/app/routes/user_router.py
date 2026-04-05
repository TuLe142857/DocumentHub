from typing import Annotated

from fastapi import APIRouter, Form

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.core.sercurity.jwt import AccessToken, OptionalAccessToken
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.user_profile_schema import (
    AvatarUpdateRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from app.services.document_service import DocumentServiceDep
from app.services.user_service import UserServiceDep

router = APIRouter(prefix="/users", tags=["UserProfile"])


@router.get("/me/profile", response_model=ResponseSuccessSchema[UserProfileResponse])
def get_self_profile(
    access_token: AccessToken,
    user_service: UserServiceDep,
):
    user_id = int(access_token.sub)
    profile = user_service.get_profile_by_id(user_id)
    res = UserProfileResponse.model_validate(profile)
    return APIResponse.ok(data=res)


@router.patch("/me/profile", response_model=ResponseSuccessSchema)
def update_self_profile(
    access_token: AccessToken,
    body: UserProfileUpdateRequest,
    user_service: UserServiceDep,
):
    user_id = int(access_token.sub)
    profile_update_dict = body.model_dump(exclude_unset=True)
    user_service.update_profile(user_id, profile_update_dict)
    return APIResponse.ok(message=f"{profile_update_dict}")


@router.put("/me/avatar", response_model=ResponseSuccessSchema)
def update_avatar(
    access_token: AccessToken,
    form: Annotated[AvatarUpdateRequest, Form(media_type="multipart/form-data")],
    user_service: UserServiceDep,
):
    user_id = int(access_token.sub)
    avatar_file = form.avatar.file
    avatar_content_type = form.avatar.content_type
    user_service.update_avatar(user_id, avatar_file, avatar_content_type)
    return APIResponse.ok(data=form.avatar.filename)


@router.get(
    "/{username}/profile", response_model=ResponseSuccessSchema[UserProfileResponse]
)
def get_userprofile(
    username: str,
    user_service: UserServiceDep,
):
    profile = user_service.get_profile_by_name(username)
    res = UserProfileResponse.model_validate(profile)
    return APIResponse.ok(data=res)


@router.get(
    "/{username}/documents",
    response_model=ResponsePaginationSchema[DocumentSummaryResponse],
)
def get_user_documents(
    username: str,
    pagination: PaginationQueryDep,
    access_token: OptionalAccessToken,
    document_service: DocumentServiceDep,
):
    if access_token is None:
        doc_list, total = document_service.list_public_document(
            owner=username, page=pagination.page, limit=pagination.limit
        )
    else:
        user_id = int(access_token.sub)
        doc_list, total = document_service.get_document_list(
            owner=username, viewer=user_id, page=pagination.page, limit=pagination.limit
        )

    res_data = [DocumentSummaryResponse.model_validate(doc) for doc in doc_list]
    return APIResponse.paginate(
        current_page=pagination.page,
        per_page=pagination.limit,
        total_items=total,
        data=res_data,
    )
