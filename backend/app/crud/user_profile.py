from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import DBSessionDep
from app.models import UserProfile

from .base import CRUDBase


class CRUDUserProfile(CRUDBase[UserProfile, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(model=UserProfile, db_session=db_session)

    def get_by_user_id(self, user_id: int) -> UserProfile | None:
        return self.db_session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        ).scalar_one_or_none()


def get_crud_user_profile(db_session: DBSessionDep) -> CRUDUserProfile:
    return CRUDUserProfile(db_session)


CRUDUserProfileDep = Annotated[CRUDUserProfile, Depends(get_crud_user_profile)]
