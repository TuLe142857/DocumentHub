from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import APIResponse, ErrorCode, ResponseErrorSchema, ResponseSuccessSchema
from app.dependencies import (
    AccessTokenDep,
    AuthServiceDep,
    DBSessionDep,
    RefreshTokenDep,
)
from app.models import User
from app.schemas.request.auth_request import *
from app.schemas.response.auth_response import *
from app.schemas.user_schema import UserSchema

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/whoami")
def whoami(access_token: AccessTokenDep, db_session: DBSessionDep):
    user_id = str(access_token.get("sub"))
    user = db_session.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    ).scalar_one_or_none()
    if user and user.role:
        res = UserSchema.model_validate(user)
        return APIResponse.ok(data=res)
    else:
        return APIResponse.error(
            ErrorCode.INVALID_CREDENTIALS,
            message=f"Invalid credentials. {type(user)}{type(user.role)}",
        )


@router.post("/register/request", response_model=ResponseSuccessSchema[None])
def request_registration(json_body: RegistrationRequest, auth_service: AuthServiceDep):
    auth_service.request_registration(**json_body.model_dump())
    return APIResponse.ok()


@router.post(
    "/register/verify", response_model=ResponseSuccessSchema[VerifyRegistrationResponse]
)
def verify_registration(body: VerifyRegistrationRequest, auth_service: AuthServiceDep):
    registration_token = auth_service.verify_registration(**body.model_dump())
    response_data = VerifyRegistrationResponse(registration_token=registration_token)
    return APIResponse.ok(data=response_data)


@router.post(
    "/register/complete",
    response_model=ResponseSuccessSchema,
    description="Complete registration and automatic login",
)
def complete_registration(
    body: CompleteRegistrationRequest, auth_service: AuthServiceDep
):
    access_token, refresh_token = auth_service.complete_registration(
        **body.model_dump()
    )
    return (
        APIResponse.ok(message="Completed registration. Automatic login.")
        .set_access_cookie(access_token)
        .set_refresh_cookie(refresh_token)
    )


@router.post("/login", response_model=ResponseSuccessSchema)
def login(body: LoginRequest, auth_service: AuthServiceDep):
    access_token, refresh_token = auth_service.login(**body.model_dump())
    return (
        APIResponse.ok()
        .set_access_cookie(access_token)
        .set_refresh_cookie(refresh_token)
    )


@router.post("/logout", response_model=ResponseSuccessSchema)
def logout():
    return APIResponse.ok().delete_access_cookie().delete_refresh_cookie()


@router.post(
    "/refresh",
    response_model=ResponseSuccessSchema,
    description="Require refresh token cookie",
)
def refresh_access_token(refresh_token: RefreshTokenDep, auth_service: AuthServiceDep):
    access_token = auth_service.refresh_access_token(refresh_token)
    return APIResponse.ok().set_access_cookie(access_token)


@router.post("/forgot_password", response_model=ResponseSuccessSchema)
def forgot_password(body: ForgotPasswordRequest, auth_service: AuthServiceDep):
    auth_service.forgot_password(**body.model_dump())
    return APIResponse.ok()


@router.post("/reset_password", response_model=ResponseSuccessSchema)
def reset_password(body: ResetPasswordRequest, auth_service: AuthServiceDep):
    auth_service.reset_password(**body.model_dump())
    return APIResponse.ok()
