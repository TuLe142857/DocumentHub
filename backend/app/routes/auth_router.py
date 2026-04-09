from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import APIResponse, ErrorCode, ResponseSuccessSchema
from app.core.sercurity import (
    AccessPayloadProvider,
    JWTPayload,
    RefreshPayloadProvider,
)
from app.schemas.auth_schema import *
from app.services.auth_service import (
    AuthServiceDep,
    CurrentUserDep,
    OptionalCurrentUserDep,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/whoami",
    response_model=ResponseSuccessSchema[SelfInfoResponse],
    summary="Get self info(require login)",
)
def whoami(user: CurrentUserDep):
    res = SelfInfoResponse.model_validate(user)
    return APIResponse.ok(data=res)


@router.post(
    "/register/request",
    response_model=ResponseSuccessSchema,
    summary="Request registration, provide email to get otp code",
)
def request_registration(json_body: RegistrationRequest, auth_service: AuthServiceDep):
    auth_service.request_registration(**json_body.model_dump())
    return APIResponse.ok()


@router.post(
    "/register/verify",
    response_model=ResponseSuccessSchema[VerifyRegistrationResponse],
    summary="Verify by otp code received from email",
)
def verify_registration(body: VerifyRegistrationRequest, auth_service: AuthServiceDep):
    registration_token = auth_service.verify_registration(**body.model_dump())
    response_data = VerifyRegistrationResponse(registration_code=registration_token)
    return APIResponse.ok(data=response_data)


@router.post(
    "/register/complete",
    response_model=ResponseSuccessSchema,
    summary="Complete registration and automatic login",
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


@router.post(
    "/login",
    response_model=ResponseSuccessSchema[LoginResponse],
    summary="Login",
    description="Write JWT token to cookie(for web client) and return token in response data(for mobile client)",
)
def login(body: LoginRequest, auth_service: AuthServiceDep):
    access_token, refresh_token = auth_service.login(**body.model_dump())
    response_data = LoginResponse(
        access_token=access_token, refresh_token=refresh_token
    )

    return (
        APIResponse.ok(data=response_data)
        .set_access_cookie(access_token)
        .set_refresh_cookie(refresh_token)
    )


@router.post("/logout", response_model=ResponseSuccessSchema)
def logout(
    access_payload: Annotated[
        JWTPayload | None,
        Depends(AccessPayloadProvider(optional=True, on_expired_action="set_none")),
    ],
    refresh_payload: Annotated[
        JWTPayload | None,
        Depends(RefreshPayloadProvider(optional=True, on_expired_action="set_none")),
    ],
    auth_service: AuthServiceDep,
):
    """
    Logout and revoke(add to jwt black list) access_token, refresh_token (if provided).
    Delete access/refresh token stored on cookie.
        - Access token(optional) can be provided via Header or Cookie
        - Refresh token(optional) can be provided via Body or Cookie

    """
    debug = {}
    if access_payload is not None:
        auth_service.revoke_token(access_payload)
        debug["access_revoked"] = True
    if refresh_payload is not None:
        auth_service.revoke_token(refresh_payload)
        debug["refresh_revoked"] = True
    return (
        APIResponse.ok(message=str(debug))
        .delete_access_cookie()
        .delete_refresh_cookie()
    )


@router.post(
    "/refresh",
    response_model=ResponseSuccessSchema[str],
    summary="Refresh Access Token",
    description="Write access token to cookie(for web client) and return access token in response data(for mobile client)",
)
def refresh_access_token(
    refresh_token: Annotated[JWTPayload, Depends(RefreshPayloadProvider())],
    auth_service: AuthServiceDep,
):
    access_token = auth_service.refresh_access_token(refresh_token)
    return APIResponse.ok(data=access_token).set_access_cookie(access_token)


@router.post(
    "/forgot_password",
    response_model=ResponseSuccessSchema,
    summary="Forgot password, get otp from mail",
)
def forgot_password(body: ForgotPasswordRequest, auth_service: AuthServiceDep):
    auth_service.forgot_password(**body.model_dump())
    return APIResponse.ok()


@router.post(
    "/reset_password",
    response_model=ResponseSuccessSchema,
    summary="Reset password by otp from mail",
)
def reset_password(body: ResetPasswordRequest, auth_service: AuthServiceDep):
    auth_service.reset_password(**body.model_dump())
    return APIResponse.ok()
