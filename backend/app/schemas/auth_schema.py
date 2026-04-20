from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MeResponse(BaseModel):
    """
    /api/auth/whoami
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")
    avatar_url: Annotated[str | None, Field(default=None)]
    role: Annotated[str, Field(validation_alias="role_name")]
    username: Annotated[str, Field()]
    email: Annotated[str, Field()]


class RegisterRequest(BaseModel):
    """
    /api/auth/register/request
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]


class RegisterVerifyRequest(BaseModel):
    """
    /api/auth/register/verify
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]
    otp_code: Annotated[str, Field()]


class RegisterVerifyResponse(BaseModel):
    """
    /api/auth/register/verify
    """

    model_config = ConfigDict(extra="ignore")
    registration_code: Annotated[str, Field()]


class RegisterCompleteRequest(BaseModel):
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


class LoginResponse(BaseModel):
    access_token: Annotated[str, Field()]
    refresh_token: Annotated[str, Field()]


class PasswordForgotRequest(BaseModel):
    """
    /api/auth/forgot_password
    """

    model_config = ConfigDict(extra="forbid")

    identity: Annotated[str, Field(description="username or email")]


class PasswordResetRequest(BaseModel):
    """
    /api/auth/reset_password
    """

    model_config = ConfigDict(extra="forbid")

    identity: Annotated[str, Field(description="username or email")]
    otp_code: Annotated[str, Field()]
    new_password: Annotated[str, Field(min_length=8, max_length=16)]
