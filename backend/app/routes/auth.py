from fastapi import APIRouter

from app.core import APIResponse, ResponseErrorSchema, ResponseSuccessSchema
from app.dependencies import AuthServiceDep
from app.schemas.request.auth_request import *
from app.schemas.response.auth_response import *

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/whoami")
def whoami():
    pass


@router.post("/register/request", response_model=ResponseSuccessSchema[None])
def request_registration(json_body: RegistrationRequest, auth_service: AuthServiceDep):
    auth_service.request_registration(**json_body.model_dump())
    return APIResponse.ok()


@router.post(
    "/register/verify", response_model=ResponseSuccessSchema[VerifyRegistrationResponse]
)
def verify_registration(body: VerifyRegistrationRequest):
    return APIResponse.ok(
        data=VerifyRegistrationResponse(registration_token="kajhsdjkadh")
    )


@router.post("/register/complete")
def complete_registration(body: CompleteRegistrationRequest):
    pass


@router.post("/login")
def login(body: LoginRequest, auth_service: AuthServiceDep):
    access_token, refresh_token = auth_service.login(**body.model_dump())
    return (
        APIResponse.ok()
        .set_access_cookie(access_token)
        .set_refresh_cookie(refresh_token)
    )


@router.post("/logout")
def logout():
    return APIResponse.ok().delete_access_cookie().delete_refresh_cookie()


@router.post("/refresh")
def refresh_access_token():
    pass


@router.post("/forgot_password")
def forgot_password():
    pass


@router.post("/reset_password")
def reset_password():
    pass
