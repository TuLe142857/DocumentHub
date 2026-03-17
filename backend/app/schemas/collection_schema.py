from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models import *


class CollectionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    name: Annotated[str, Field()]


class CollectionCreateRequest(BaseModel):
    name: Annotated[str, Field()]


class CollectionRenameRequest(BaseModel):
    name: Annotated[str, Field()]
