from typing import Annotated, Any

from fastapi import UploadFile
from pydantic import AfterValidator, BaseModel, Field, computed_field

from app.models import DocumentVisibility
from app.schemas.validate import validate_file, validate_tag_name_list
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
