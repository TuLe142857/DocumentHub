from fastapi import APIRouter, Depends

from app.core import APIResponse, ErrorCode, ResponseSuccessSchema, build_error_docs
from app.core.sercurity import (
    AccessPayloadProvider,
    JWTPayload,
    RefreshPayloadProvider,
)
from app.schemas.auth_schema import *
from app.services.auth_service import (
    AuthServiceDep,
    CurrentUserDep,
)
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/whoami",
    response_model=ResponseSuccessSchema[MeResponse],
    responses=build_error_docs(
        (ErrorCode.UNAUTHORIZED, "User not login"),
    ),
    summary="Get self info(require login or return error)",
)
def whoami(user: CurrentUserDep, storage_service: StorageServiceDep):
    res = MeResponse.model_validate(user)
    if user.profile.avatar_object_key:
        res.avatar_url = storage_service.generate_image_url(
            user.profile.avatar_object_key
        )
    return APIResponse.ok(data=res)


@router.post(
    "/register/request",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        (ErrorCode.RESOURCE_ALREADY_EXISTS, "Email already exists"),
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Request registration, provide email to get otp code",
)
def request_registration(body: RegisterRequest, auth_service: AuthServiceDep):
    auth_service.request_registration(email=body.email)
    return APIResponse.ok()


@router.post(
    "/register/verify",
    response_model=ResponseSuccessSchema[RegisterVerifyResponse],
    responses=build_error_docs(
        (ErrorCode.INVALID_CODE, "OTP not match or expired"),
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Verify by otp code received from email",
)
def verify_registration(body: RegisterVerifyRequest, auth_service: AuthServiceDep):
    registration_token = auth_service.verify_registration(
        email=body.email, otp_code=body.otp_code
    )
    response_data = RegisterVerifyResponse(registration_code=registration_token)
    return APIResponse.ok(data=response_data)


@router.post(
    "/register/complete",
    response_model=ResponseSuccessSchema[LoginResponse],
    responses=build_error_docs(
        (ErrorCode.RESOURCE_ALREADY_EXISTS, "Username already exist"),
        (ErrorCode.INVALID_CODE, "Registration code not match or expired"),
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Complete registration and automatic login",
)
def complete_registration(body: RegisterCompleteRequest, auth_service: AuthServiceDep):
    access_token, refresh_token = auth_service.complete_registration(
        email=body.email,
        registration_code=body.registration_code,
        username=body.username,
        password=body.password,
    )
    res_data = LoginResponse(access_token=access_token, refresh_token=refresh_token)
    return (
        APIResponse.ok(data=res_data, message="Completed registration.")
        .set_access_cookie(access_token)
        .set_refresh_cookie(refresh_token)
    )


@router.post(
    "/login",
    response_model=ResponseSuccessSchema[LoginResponse],
    responses=build_error_docs(
        (ErrorCode.LOGIN_FAILED, "Identity or password not match"),
        (ErrorCode.USER_INACTIVE, "User is inactive(User was banned"),
        ErrorCode.VALIDATION_ERROR,
    ),
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
    responses=build_error_docs(
        (ErrorCode.JWT_TOKEN_REVOKED, "JWT Token has ben revoked"),
        (ErrorCode.JWT_TOKEN_EXPIRED, "Refresh token has be expired"),
        (ErrorCode.USER_INACTIVE, "User is inactive(User was banned)"),
    ),
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
    responses=build_error_docs(
        (ErrorCode.INVALID_CREDENTIALS, "User not found"),
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Forgot password, get otp from mail",
)
def forgot_password(body: PasswordForgotRequest, auth_service: AuthServiceDep):
    auth_service.forgot_password(**body.model_dump())
    return APIResponse.ok()


@router.post(
    "/reset_password",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        (ErrorCode.INVALID_CREDENTIALS, "User not found"),
        (ErrorCode.INVALID_CODE, "OTP code not matched or expired"),
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Reset password by otp from mail",
)
def reset_password(body: PasswordResetRequest, auth_service: AuthServiceDep):
    auth_service.reset_password(**body.model_dump())
    return APIResponse.ok()
