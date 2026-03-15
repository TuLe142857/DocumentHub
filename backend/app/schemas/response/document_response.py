from typing import Annotated

from pydantic import (
    AliasPath,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
)

from app.models import Document, DocumentLike, DocumentStatus, DocumentVisibility, Tag


class DocumentSupportedTypeResponse(BaseModel):
    supported_type: Annotated[list[str], Field()]


class DocumentSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    title: Annotated[str, Field()]
    file_thumbnail_url: Annotated[str, Field()]
    view_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]
    category: Annotated[str, Field(validation_alias=AliasPath("category", "name"))]


class DocumentDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    title: Annotated[str, Field()]
    visibility: Annotated[DocumentVisibility, Field()]
    owner: Annotated[str, Field()]
    category: Annotated[str, Field(validation_alias=AliasPath("category", "name"))]

    # convert from list[Tag] to list[str]
    tags: Annotated[list[str], BeforeValidator(lambda tags: [_.name for _ in tags])]

    desc: Annotated[str | None, Field()]

    file_type: Annotated[str, Field()]
    file_url: Annotated[str, Field()]
    file_thumbnail_url: Annotated[str, Field()]
    file_preview_url: Annotated[str, Field()]
    sha256sum: Annotated[str, Field()]
    md5sum: Annotated[str, Field()]
    page_count: Annotated[int, Field()]
    view_count: Annotated[int, Field()]
    like_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]
