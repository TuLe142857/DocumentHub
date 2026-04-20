import datetime
from typing import Annotated, Any
import re
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

from app.core import AppException, ErrorCode, PaginationQuery, get_settings
from app.models import DocumentStatus, DocumentVisibility
from app.utils import get_file_extension

def validate_file(file: UploadFile) -> UploadFile:
    filename = file.filename

    if filename is None:
        raise AppException(ErrorCode.VALIDATION_ERROR, "Invalid file name")
    try:
        extension = get_file_extension(filename)
    except ValueError:
        raise AppException(ErrorCode.VALIDATION_ERROR, "Can not detect file extension")

    settings = get_settings()
    if not extension in settings.SUPPORTED_FILE_TYPE:
        raise AppException(ErrorCode.UNSUPPORTED_FILE_TYPE, f"File extension {extension} not supported. Supported file extension: {settings.SUPPORTED_FILE_TYPE}")

    return file


def validate_tag_name(tag_name: str) -> str:
    tag_name = tag_name.strip()
    if len(tag_name) >= 50:
        raise AppException(ErrorCode.VALIDATION_ERROR, "Tag name too long, max 50 characters")
    if len(tag_name) == 0:
        raise AppException(ErrorCode.VALIDATION_ERROR, "Tag name cannot be empty")
    if (not re.fullmatch(r"[a-z0-9-_]+", tag_name)) or tag_name.startswith('-') or tag_name.startswith('_'):
        raise AppException(ErrorCode.VALIDATION_ERROR,
                           "Invalid tag name. Tag name can only contain 'a-z', '0-9', '-' and '_'. Tag name can not start with '-' or '_'")
    return tag_name

def validate_tag_name_list(tag_names: list[str]) -> list[str]:
    return [validate_tag_name(t) for t in tag_names]

class DocumentUploadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # ----------------------------------------------------
    #               FIELDS
    # ----------------------------------------------------
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


class DocumentUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str | None, Field(default=None)]
    desc: Annotated[str | None, Field(default=None)]
    category_id: Annotated[int | None, Field(default=None)]
    visibility: Annotated[DocumentVisibility | None, Field(default=None)]
    tags: Annotated[list[str] | None, Field(default=None), AfterValidator(validate_tag_name_list)]

class DocumentTagSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tag_name: Annotated[str, Field(), AfterValidator(validate_tag_name)]

class DocumentPublicQuery(PaginationQuery):
    """
    Use for GET /users/{username}/documents and GET /search
    """

    model_config = ConfigDict(extra="forbid")
    q: Annotated[
        str | None, Field(default=None, description="Search query, default None")
    ]
    types: Annotated[list[str] | None, Field(default=None, description="Document type")]
    category_ids: Annotated[list[int] | None, Field(default=None)]
    tags: Annotated[list[str] | None, Field(default=None)]
    sort: Annotated[str | None, Field(default=None)]


class DocumentOwnerQuery(PaginationQuery):
    """
    Use for GET /users/me/documents
    """

    model_config = ConfigDict(extra="forbid")
    q: Annotated[
        str | None, Field(default=None, description="Search query, default None")
    ]
    types: Annotated[list[str] | None, Field(default=None, description="Document type")]
    category_ids: Annotated[list[int] | None, Field(default=None)]
    tags: Annotated[list[str] | None, Field(default=None)]
    sort: Annotated[str | None, Field(default=None)]

    statuses: Annotated[
        list[DocumentStatus] | None, Field(default=[DocumentStatus.READY])
    ]
    visibility: Annotated[DocumentVisibility | None, Field(default=None)]


class DocumentSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: Annotated[int, Field()]
    title: Annotated[str, Field()]
    file_thumbnail_url: Annotated[str, Field(default="")]
    file_type: Annotated[str, Field(description="Original file type")]
    visibility: Annotated[DocumentVisibility, Field()]
    status: Annotated[DocumentStatus, Field()]
    owner: Annotated[
        str,
        Field(
            validation_alias=AliasPath("owner", "username"),
            description="owner username",
        ),
    ]
    page_count: Annotated[int, Field()]
    view_count: Annotated[int, Field()]
    like_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]
    category: Annotated[
        str,
        Field(
            validation_alias=AliasPath("category", "name"), description="category name"
        ),
    ]
    tags: Annotated[
        list[str],
        Field(description="tag name"),
        BeforeValidator(lambda tags: [_.name for _ in tags]),
    ]

    created_at: Annotated[datetime.datetime, Field()]

    @staticmethod
    def build(from_obj: Any, thumbnail_url: str) -> "DocumentSummarySchema":
        """ "
        Build a DocumentSummaryResponse from object.
        This method use pydantic BaseModel.model_validate() and override attribute file_thumbnail_url.
        """
        res = DocumentSummarySchema.model_validate(from_obj)
        res.file_thumbnail_url = thumbnail_url
        return res


class DocumentDetailsSchema(DocumentSummarySchema):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    desc: Annotated[str | None, Field()]
    file_preview_url: Annotated[
        str, Field(default="", description="Preview version(PDF)")
    ]
    liked: Annotated[
        bool,
        Field(
            default=False,
            description="Whether or not the document was liked by current user",
        ),
    ]

    @computed_field(description="Available formats for download document. ")
    def available_formats(self) -> list[str]:
        if self.file_type == ".pdf":
            return [".pdf"]
        return [".pdf", self.file_type]

    sha256sum: Annotated[str, Field()]
    md5sum: Annotated[str, Field()]

    @staticmethod
    def build(
        from_obj: Any, thumbnail_url: str, preview_url: str, liked: bool = False
    ) -> "DocumentDetailsSchema":
        """
        Build a DocumentDetailsResponse from object.
        This method use pydantic BaseModel.model_validate() and override attribute file_thumbnail_url,
        file_preview_url and liked.
        """
        res = DocumentDetailsSchema.model_validate(from_obj)
        res.file_thumbnail_url = thumbnail_url
        res.file_preview_url = preview_url
        res.liked = liked
        return res
