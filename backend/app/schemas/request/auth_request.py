from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]


class VerifyRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]
    otp_code: Annotated[str, Field()]


class CompleteRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, EmailStr]
    registration_code: Annotated[str, Field()]
    username: Annotated[str, Field()]
    password: Annotated[str, Field(min_length=8, max_length=16)]


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: Annotated[str, Field(description="username or email")]
    password: Annotated[str, Field()]
