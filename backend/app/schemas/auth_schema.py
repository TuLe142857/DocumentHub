from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SelfInfoResponse(BaseModel):
    """
    /api/auth/whoami
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")
    role: Annotated[str, Field(validation_alias="role_name")]
    username: Annotated[str, Field()]
    email: Annotated[str, Field()]


class RegistrationRequest(BaseModel):
    """
    /api/auth/register/request
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]


class VerifyRegistrationResponse(BaseModel):
    """
    /api/auth/register/verify
    """

    registration_token: Annotated[str, Field()]


class VerifyRegistrationRequest(BaseModel):
    """
    /api/auth/register/verify
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]
    otp_code: Annotated[str, Field()]


class CompleteRegistrationRequest(BaseModel):
    """
    /api/auth/register/complete
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]
    registration_code: Annotated[str, Field()]
    username: Annotated[str, Field()]
    password: Annotated[str, Field(min_length=8, max_length=16)]


class LoginRequest(BaseModel):
    """
    /api/auth/login
    """

    model_config = ConfigDict(extra="forbid")

    identity: Annotated[str, Field(description="username or email")]
    password: Annotated[str, Field()]


class ForgotPasswordRequest(BaseModel):
    """
    /api/auth/forgot_password
    """

    model_config = ConfigDict(extra="forbid")

    identity: Annotated[str, Field(description="username or email")]


class ResetPasswordRequest(BaseModel):
    """
    /api/auth/reset_password
    """

    model_config = ConfigDict(extra="forbid")

    identity: Annotated[str, Field(description="username or email")]
    otp_code: Annotated[str, Field()]
    new_password: Annotated[str, Field(min_length=8, max_length=16)]
