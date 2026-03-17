from typing import Annotated, Any

from fastapi import UploadFile
from pydantic import (
    AfterValidator,
    AliasPath,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    computed_field,
)

from app.core import get_settings
from app.models import DocumentStatus, DocumentVisibility
from app.schemas.validate import validate_file, validate_s3_url, validate_tag_name_list
from app.utils import get_file_extension, md5_checksum, sha256_checksum


class DocumentUploadFormRequest(BaseModel):
    file: Annotated[UploadFile, Field(), AfterValidator(validate_file)]

    title: Annotated[str, Field()]
    category_id: Annotated[int, Field()]
    visibility: Annotated[DocumentVisibility, Field(default=DocumentVisibility.PUBLIC)]
    desc: Annotated[str | None, Field(default=None)]

    tags: Annotated[
        list[str], Field(default=[]), AfterValidator(validate_tag_name_list)
    ]

    @computed_field
    @property
    def file_type(self) -> str:
        return get_file_extension(self.file.filename)

    @computed_field
    @property
    def sha256sum(self) -> str:
        return sha256_checksum(self.file.file)

    @computed_field
    @property
    def md5checksum(self) -> str:
        return md5_checksum(self.file.file)


class DocumentUpdateRequest(BaseModel):
    model_config = ConfigDict()
    desc: Annotated[str | None, Field(default=None)]
    title: Annotated[str | None, Field(default=None)]
    category_id: Annotated[int | None, Field(default=None)]
    visibility: Annotated[DocumentVisibility | None, Field(default=None)]


class DocumentSupportedTypeResponse(BaseModel):
    supported_type: Annotated[list[str], Field()]


class DocumentSummaryResponse(BaseModel):
    FILE_URL_VALIDATOR = validate_s3_url(
        bucket=get_settings().S3_DOCUMENTS_BUCKET,
        expires_in=5 * 60,
        base_url=get_settings().S3_PUBLIC_URL_OVERRIDE,
    )

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: Annotated[int, Field()]
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


class DocumentDetailsResponse(DocumentSummaryResponse):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    desc: Annotated[str | None, Field()]

    file_original_url: Annotated[
        str,
        Field(validation_alias="file_object_key"),
        BeforeValidator(DocumentSummaryResponse.FILE_URL_VALIDATOR),
    ]

    file_preview_url: Annotated[
        str,
        Field(validation_alias="file_preview_object_key"),
        BeforeValidator(DocumentSummaryResponse.FILE_URL_VALIDATOR),
    ]
    sha256sum: Annotated[str, Field()]
    md5sum: Annotated[str, Field()]
    page_count: Annotated[int, Field()]
    view_count: Annotated[int, Field()]
    like_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]
