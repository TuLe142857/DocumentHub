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

from app.core import AppException, ErrorCode, PaginationQuery, get_settings
from app.models import DocumentStatus, DocumentVisibility
from app.utils import get_file_extension, md5_checksum, sha256_checksum


class DocumentUploadFormRequest(BaseModel):
    # ----------------------------------------------------
    #               CUSTOM VALIDATOR
    # ----------------------------------------------------
    @staticmethod
    def validate_file_name(file_name: str) -> str:
        settings = get_settings()
        index = file_name.rfind(".")
        if index == -1:
            raise AppException(
                ErrorCode.UNSUPPORTED_FILE_TYPE,
                f"Can not find file extension in filename '{file_name}'",
            )
        extension = file_name[index::]
        if extension not in settings.SUPPORTED_FILE_TYPE:
            raise AppException(
                ErrorCode.UNSUPPORTED_FILE_TYPE,
                f"File extension '{extension}' not supported",
            )
        return file_name

    @staticmethod
    def validate_file(file: UploadFile) -> UploadFile:
        DocumentUploadFormRequest.validate_file_name(file.filename)
        return file

    @staticmethod
    def validate_tag_name(tag_name: str) -> str:
        tag_name = tag_name.strip()
        if " " in tag_name:
            raise AppException(
                ErrorCode.VALIDATION_ERROR, f"Tag name cannot contain spaces {tag_name}"
            )
        if not tag_name.islower():
            raise AppException(
                ErrorCode.VALIDATION_ERROR, "Tag name cannot contain uppercase"
            )
        return tag_name

    @staticmethod
    def validate_tag_name_list(tag_names: list[str]) -> list[str]:
        return [DocumentUploadFormRequest.validate_tag_name(_) for _ in tag_names]

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
    tags: Annotated[list[str] | None, Field(default=None)]


class DocumentSupportedTypeResponse(BaseModel):
    supported_type: Annotated[list[str], Field()]


class DocumentQuery(PaginationQuery):
    status: Annotated[DocumentStatus | None, Field(default=None)]


class DocumentSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: Annotated[int, Field()]
    title: Annotated[str, Field()]
    visibility: Annotated[DocumentVisibility, Field()]
    status: Annotated[DocumentStatus, Field]

    # Flatten User object to its username string
    owner: Annotated[
        str,
        Field(
            validation_alias=AliasPath("owner", "username"),
            description="owner username",
        ),
    ]

    file_thumbnail_url: Annotated[
        str,
        Field(validation_alias="thumbnail_object_key"),
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

    file_type: Annotated[str, Field(description="Original file type")]

    @staticmethod
    def from_object(obj: Any, thumbnail_url: str) -> "DocumentSummaryResponse":
        res = DocumentSummaryResponse.model_validate(obj)
        res.file_thumbnail_url = thumbnail_url
        return res


class DocumentDetailsResponse(DocumentSummaryResponse):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    liked: Annotated[
        bool,
        Field(
            default=False,
            description="Whether or not the document was liked by current user",
        ),
    ]
    desc: Annotated[str | None, Field()]
    #
    # file_original_url: Annotated[
    #     str,
    #     Field(validation_alias="file_object_key"),
    # ]

    file_preview_url: Annotated[
        str,
        Field(validation_alias="file_preview_object_key"),
    ]

    @computed_field(description="Available formats for download document. ")
    def available_formats(self) -> list[str]:
        if self.file_type == ".pdf":
            return [".pdf"]
        return [".pdf", self.file_type]

    sha256sum: Annotated[str, Field()]
    md5sum: Annotated[str, Field()]
    page_count: Annotated[int, Field()]
    view_count: Annotated[int, Field()]
    like_count: Annotated[int, Field()]
    download_count: Annotated[int, Field()]

    @staticmethod
    def from_object(
        obj: Any, thumbnail_url: str, preview_url: str
    ) -> "DocumentDetailsResponse":
        res = DocumentDetailsResponse.model_validate(obj)
        res.file_thumbnail_url = thumbnail_url
        res.file_preview_url = preview_url
        # res.file_original_url = original_url
        return res
