from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class VerifyRegistrationResponse(BaseModel):
    registration_token: Annotated[str, Field()]


class SelfProfileResponse(BaseModel):
    """
    Response for /api/auth/whoami
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")
    role: Annotated[str, Field(validation_alias="role_name")]
    username: Annotated[str, Field()]
    email: Annotated[str, Field()]
