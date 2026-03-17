from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

class CategorySchema(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: Annotated[int, Field()]
    name: Annotated[str, Field()]