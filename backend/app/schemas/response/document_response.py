from typing import Annotated

from pydantic import (
    AliasPath,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
)

from app.core import get_settings
from app.models import DocumentStatus, DocumentVisibility
from app.schemas.validate import validate_s3_url


class DocumentSupportedTypeResponse(BaseModel):
    supported_type: Annotated[list[str], Field()]


class DocumentSummaryResponse(BaseModel):
    FILE_URL_VALIDATOR = validate_s3_url(
        bucket=get_settings().S3_DOCUMENTS_BUCKET,
        expires_in=5 * 60,
        base_url=get_settings().S3_PUBLIC_URL_OVERRIDE,
    )

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    title: Annotated[str, Field()]
    visibility: Annotated[DocumentVisibility, Field()]
    status: Annotated[DocumentStatus, Field]

    # Flatten User object to its username string
    owner: Annotated[
        str,
        Field(description="owner username"),
        BeforeValidator(lambda owner: owner.username),
    ]

    file_thumbnail_url: Annotated[
        str,
        Field(validation_alias="thumbnail_object_key"),
        BeforeValidator(FILE_URL_VALIDATOR),
    ]

    view_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]

    # Access category name via nested relationship path: category.name
    category: Annotated[
        str,
        Field(
            validation_alias=AliasPath("category", "name"), description="category name"
        ),
    ]

    # Flatten List[Tag objects] into a List[str]
    tags: Annotated[
        list[str],
        Field(description="tag name"),
        BeforeValidator(lambda tags: [_.name for _ in tags]),
    ]

    file_type: Annotated[str, Field()]

    file_preview_url: Annotated[
        str,
        Field(validation_alias="file_preview_object_key"),
        BeforeValidator(FILE_URL_VALIDATOR),
    ]


class DocumentDetailsResponse(DocumentSummaryResponse):
    desc: Annotated[str | None, Field()]

    file_original_url: Annotated[
        str,
        Field(validation_alias=""),
        BeforeValidator(DocumentSummaryResponse.FILE_URL_VALIDATOR),
    ]

    file_preview_url: Annotated[
        str,
        Field(validation_alias=""),
        BeforeValidator(DocumentSummaryResponse.FILE_URL_VALIDATOR),
    ]
    sha256sum: Annotated[str, Field()]
    md5sum: Annotated[str, Field()]
    page_count: Annotated[int, Field()]
    view_count: Annotated[int, Field()]
    like_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]
