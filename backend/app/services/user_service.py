from typing import Annotated, BinaryIO, Sequence

from fastapi import Depends
from mypy_boto3_s3 import S3Client
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode, get_settings
from app.crud.user import CRUDUser, CRUDUserDep
from app.crud.user_profile import CRUDUserProfile, CRUDUserProfileDep
from app.dependencies import DBSessionDep, S3Dep
from app.models import *


class UserService:
    def __init__(
        self,
        crud_user: CRUDUser,
        crud_profile: CRUDUserProfile,
        db_session: Session,
        s3_client: S3Client,
    ):
        self.crud_user = crud_user
        self.crud_profile = crud_profile
        self.db_session = db_session
        self.s3_client = s3_client

    def list_user(
        self,
        filter_email: str | None = None,
        filter_name: str | None = None,
        filter_is_active: bool | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[Sequence[User], int]:

        role_id_user = Role.get_or_create("USER", self.db_session).id
        stmt = select(User).where(User.role_id == role_id_user)

        if filter_email is not None:
            stmt = stmt.where(User.email.like(f"%{filter_email}%"))
        if filter_name is not None:
            stmt = stmt.where(User.username.like(f"%{filter_name}%"))
        if filter_is_active is not None:
            stmt = stmt.where(User.is_active == filter_is_active)

        # count
        total_count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or None
        )

        if total_count == 0:
            return [], 0

        # query
        res = (
            self.db_session.execute(stmt.offset((page - 1) * limit).limit(limit))
            .scalars()
            .all()
        )
        return res, total_count

    def get_by_id(self, user_id: int) -> User:
        return self.crud_user.get(
            user_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )

    def get_user_by_name(self, username: str) -> User:
        user = self.db_session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if user is None:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")
        return user

    def get_profile_by_id(self, user_id: int) -> UserProfile:
        profile = self.crud_profile.get_by_user_id(user_id)
        if profile is None:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")
        return profile

    def get_profile_by_name(self, username: str) -> UserProfile:
        profile = self.db_session.execute(
            select(UserProfile).join(User).where(User.username == username)
        ).scalar_one_or_none()
        if profile is None:
            raise AppException(ErrorCode.INVALID_CREDENTIALS, "User not found")
        return profile

    def update_profile(self, user_id: int, update_dict: dict):
        profile = self.get_profile_by_id(user_id)
        self.crud_profile.update(profile, update_dict)

    def update_avatar(self, user_id: int, new_avatar: BinaryIO, content_type: str):
        user = self.crud_user.get(
            user_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )
        avatar_obj_key = f"avatar/{user_id}"

        # upload to s3
        self.s3_client.upload_fileobj(
            new_avatar,
            Bucket=get_settings().S3_IMAGES_BUCKET,
            Key=avatar_obj_key,
            ExtraArgs={"ContentType": content_type},
        )

        # update user profile

        profile = self.crud_profile.get_by_user_id(user_id)
        profile.avatar_object_key = avatar_obj_key
        self.db_session.flush()

    def ban_user(self, user_id: int, admin_id: int, reason: str):
        user = self.crud_user.get(
            user_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )
        user.is_active = False
        # send email ....

    def unban_user(self, user_id: int, admin_id: int):
        user = self.crud_user.get(
            user_id,
            on_not_found=AppException(ErrorCode.INVALID_CREDENTIALS, "User not found"),
        )
        user.is_active = True
        # send email ....


def get_user_service(
    crud_user: CRUDUserDep,
    crud_profile: CRUDUserProfileDep,
    db_session: DBSessionDep,
    s3_client: S3Dep,
) -> UserService:
    return UserService(crud_user, crud_profile, db_session, s3_client)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
