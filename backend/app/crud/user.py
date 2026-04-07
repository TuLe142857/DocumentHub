from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core import AppException
from app.dependencies import DBSessionDep
from app.models import User

from .base import CRUDBase


class CRUDUser(CRUDBase[User, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(model=User, db_session=db_session)

    def get_by_identity(
        self, identity: str, *, on_not_found: AppException | None = None
    ) -> User | None:
        """
        Select User by username or email. Raise exception if not found(optional, must provide `on_not_found` as an Exception).
        Args:
            identity: email or username
            on_not_found: AppException or None. If provide an AppException instance, it will be raised when user not found.
        Returns:
            User|None: user or None
        Raises:
            AppException: when user does not exist and `on_not_found` is provided as AppException instance.
        """
        user = self.db_session.execute(
            select(User).where(or_(User.email == identity, User.username == identity))
        ).scalar_one_or_none()
        if user is None and on_not_found is not None:
            raise on_not_found
        return user


def get_crud_user(db_session: DBSessionDep) -> CRUDUser:
    return CRUDUser(db_session=db_session)


CRUDUserDep = Annotated[CRUDUser, Depends(get_crud_user)]
