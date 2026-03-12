import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, SecretStr, computed_field

from app.models import Gender, Role


class RoleSchema(BaseModel):
    """
    Schema for Role model
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: Annotated[int, Field()]
    name: Annotated[str, Field()]


class UserSchema(BaseModel):
    """
    Schema for User model
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")
    role: Annotated[str, Field(validation_alias="role_name")]
    username: Annotated[str, Field()]
    email: Annotated[str, Field()]


class UserProfileSchema(BaseModel):
    """
    Schema for UserProfile model
    """

    user_id: Annotated[int, Field()]
    avatar_object_key: Annotated[str, Field()]
    full_name: Annotated[str, Field()]
    gender: Annotated[Gender, Field()]
    phone_number: Annotated[str, Field()]
    bio: Annotated[str, Field()]
