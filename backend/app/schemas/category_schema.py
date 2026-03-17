from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CategorySchema(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: Annotated[int, Field()]
    name: Annotated[str, Field()]
