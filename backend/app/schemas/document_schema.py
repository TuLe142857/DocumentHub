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
    status: Annotated[DocumentStatus | None, Field(default=DocumentStatus.READY)]


class DocumentSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: Annotated[int, Field()]
    title: Annotated[str, Field()]
    file_thumbnail_url: Annotated[str, Field(default="")]
    file_type: Annotated[str, Field(description="Original file type")]
    visibility: Annotated[DocumentVisibility, Field()]
    status: Annotated[DocumentStatus, Field]
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

    @staticmethod
    def build(from_obj: Any, thumbnail_url: str) -> "DocumentSummaryResponse":
        """ "
        Build a DocumentSummaryResponse from object.
        This method use pydantic BaseModel.model_validate() and override attribute file_thumbnail_url.
        """
        res = DocumentSummaryResponse.model_validate(from_obj)
        res.file_thumbnail_url = thumbnail_url
        return res


class DocumentDetailsResponse(DocumentSummaryResponse):
    file_thumbnail_url: Annotated[str, Field(default=None)]
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
    ) -> "DocumentDetailsResponse":
        """
        Build a DocumentDetailsResponse from object.
        This method use pydantic BaseModel.model_validate() and override attribute file_thumbnail_url,
        file_preview_url and liked.
        """
        res = DocumentDetailsResponse.model_validate(from_obj)
        res.file_thumbnail_url = thumbnail_url
        res.file_preview_url = preview_url
        res.liked = liked
        return res
