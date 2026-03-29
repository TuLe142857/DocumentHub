from typing import Annotated

from fastapi import UploadFile
from pydantic import AfterValidator, AliasPath, BaseModel, ConfigDict, Field

from app.core import AppException, ErrorCode, PaginationQuery, get_settings
from app.models import Gender
from app.schemas.validate import validate_s3_url
from app.utils import get_file_extension


class UserProfileResponse(BaseModel):
    @staticmethod
    def convert_avatar_object_key(v: str | None) -> str | None:
        validator = validate_s3_url(
            bucket=get_settings().S3_IMAGES_BUCKET,
            expires_in=5 * 60,
            base_url=get_settings().S3_PUBLIC_URL_OVERRIDE,
        )
        if v is None:
            return v
        return validator(v)

    model_config = ConfigDict(from_attributes=True)

    username: Annotated[str, Field(validation_alias=AliasPath("user", "username"))]
    avatar_url: Annotated[
        str | None,
        Field(validation_alias="avatar_object_key"),
        AfterValidator(convert_avatar_object_key),
    ]
    full_name: Annotated[str | None, Field()]
    gender: Annotated[Gender | None, Field()]
    phone_number: Annotated[str | None, Field()]
    bio: Annotated[str | None, Field()]


class UserProfileUpdateRequest(BaseModel):
    full_name: Annotated[str | None, Field(default=None)]
    gender: Annotated[Gender | None, Field(default=None)]
    phone_number: Annotated[str | None, Field(default=None)]
    bio: Annotated[str | None, Field(default=None)]


class AvatarUpdateRequest(BaseModel):
    @staticmethod
    def validate_image_file_extension(file: UploadFile):
        file_name = file.filename
        file_ext = get_file_extension(file_name)
        if not (file_ext in [".png", ".jpg", ".jpeg"]):
            raise AppException(
                ErrorCode.UNSUPPORTED_FILE_TYPE, f"Invalid image type '{file_ext}'"
            )

        return file

    avatar: Annotated[
        UploadFile, Field(), AfterValidator(validate_image_file_extension)
    ]
