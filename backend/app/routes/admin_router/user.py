from typing import Annotated

from fastapi import APIRouter, Body, Query

from app.core import (
    APIResponse,
    AppException,
    ErrorCode,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.core.sercurity import AccessToken
from app.schemas.user_schema import UserSchema, UserSearchQuery
from app.services.auth_service import AuthServiceDep
from app.services.user_service import UserServiceDep

router = APIRouter(prefix="/users")


@router.get("", response_model=ResponsePaginationSchema[UserSchema])
def get_user_list(
    # access_token: AccessToken,
    query: Annotated[UserSearchQuery, Query()],
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
):
    # if not auth_service.is_admin(int(access_token.sub)):
    #     raise AppException(ErrorCode.FORBIDDEN)
    users, total = user_service.list_user(
        filter_email=query.email,
        filter_name=query.username,
        filter_is_active=query.is_active,
        page=query.page,
        limit=query.limit,
    )

    res_data = [UserSchema.model_validate(user) for user in users]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res_data,
    )


@router.post("/{user_id}/ban", response_model=ResponseSuccessSchema)
def ban(
    user_id: int,
    reason: Annotated[str, Body()],
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN)
    user_service.ban_user(user_id, admin_id=int(access_token.sub), reason=reason)
    return APIResponse.ok()


@router.post("/{user_id}/unban", response_model=ResponseSuccessSchema)
def unban(
    user_id: int,
    access_token: AccessToken,
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
):
    if not auth_service.is_admin(int(access_token.sub)):
        raise AppException(ErrorCode.FORBIDDEN)
    user_service.unban_user(user_id, admin_id=int(access_token.sub))
    return APIResponse.ok()
