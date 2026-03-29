from fastapi import APIRouter, Query
from typing import Annotated
from app.core import APIResponse, ResponsePaginationSchema, ResponseSuccessSchema, AppException, ErrorCode
from app.core.sercurity import AccessToken
from app.schemas.user_schema import UserSearchQuery, UserSchema
from app.services.user_service import UserServiceDep
from app.services.auth_service import AuthServiceDep
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
def ban(user_id: int):
    return APIResponse.ok()


@router.post("/{user_id}/unban", response_model=ResponseSuccessSchema)
def unban(user_id: int):
    return APIResponse.ok()
