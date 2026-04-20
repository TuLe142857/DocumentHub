from typing import Annotated, Any, Callable
from urllib.parse import urlparse

from fastapi import UploadFile
from pydantic import AfterValidator, AliasPath, BaseModel, ConfigDict, Field

from app.core import AppException, ErrorCode, PaginationQuery, get_settings
from app.dependencies import get_s3
from app.models import Gender
from app.utils import get_file_extension


class UserPrivateProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Annotated[str, Field()]
    email: Annotated[str, Field()]
    is_active: Annotated[bool, Field()]


class UserSearchQuery(PaginationQuery):
    username: Annotated[str | None, Field(default=None)]
    email: Annotated[str | None, Field(default=None)]
    is_active: Annotated[bool | None, Field(default=None)]


class UserPublicProfileSchema(BaseModel):
    @staticmethod
    def generate_s3_presigned_url(
        bucket: str,
        expires_in: int = 5 * 60,
        extra_params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> Callable[[str], str]:
        params = extra_params if (extra_params is not None) else dict()
        params["Bucket"] = bucket

        def validate_function(key: str) -> str:
            s3 = get_s3()
            params["Key"] = key
            url = s3.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expires_in,
            )
            if base_url is not None:
                parsed_url = urlparse(url)
                final_url = base_url + parsed_url.path + "?" + parsed_url.query
                return final_url
            return url

        return validate_function

    @staticmethod
    def convert_avatar_object_key(v: str | None) -> str | None:
        validator = UserPublicProfileSchema.generate_s3_presigned_url(
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
        if file_ext not in [".png", ".jpg", ".jpeg"]:
            raise AppException(
                ErrorCode.UNSUPPORTED_FILE_TYPE, f"Invalid image type '{file_ext}'"
            )

        return file

    avatar: Annotated[
        UploadFile, Field(), AfterValidator(validate_image_file_extension)
    ]
