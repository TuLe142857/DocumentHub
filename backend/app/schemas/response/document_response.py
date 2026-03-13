from typing import Annotated

from pydantic import BaseModel, Field


class DocumentSupportedTypeResponse(BaseModel):
    supported_type: Annotated[list[str], Field()]
