from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from app.core import PaginationQuery

class UserSearchQuery(PaginationQuery):
    username: Annotated[str | None, Field(default=None)]
    email: Annotated[str | None, Field(default=None)]
    is_active: Annotated[bool | None, Field(default=None)]

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Annotated[str, Field()]
    email: Annotated[str, Field()]
    is_active: Annotated[bool, Field()]