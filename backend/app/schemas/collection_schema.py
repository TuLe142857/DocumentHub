from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field


class CollectionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: Annotated[int, Field()]
    name: Annotated[str, Field()]
