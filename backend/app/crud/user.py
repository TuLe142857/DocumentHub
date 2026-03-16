from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.dependencies import DBSessionDep
from app.models import User

from .base import CRUDBase


class CRUDUser(CRUDBase[User, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(model=User, db_session=db_session)

    def get_by_identity(self, identity: str) -> User | None:
        """
        Select by username or email
        Args:
            identity: email or username

        Returns:
        """
        return self.db_session.execute(
            select(User).where(or_(User.email == identity, User.username == identity))
        ).scalar_one_or_none()


def get_crud_user(db_session: DBSessionDep) -> CRUDUser:
    return CRUDUser(db_session=db_session)


CRUDUserDep = Annotated[CRUDUser, Depends(get_crud_user)]
