from typing import Annotated

from pydantic import BaseModel, Field


class VerifyRegistrationResponse(BaseModel):
    registration_token: Annotated[str, Field()]
