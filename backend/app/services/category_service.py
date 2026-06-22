from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import AppException, ErrorCode
from app.dependencies import DBSessionDep
from app.models import Category, Document


class CategoryService:
    def __init__(
        self,
        db_session: Session,
    ):
        self.db_session = db_session

    def list_all_categories(self) -> Sequence[Category]:
        categories = self.db_session.execute(select(Category)).scalars().all()
        return categories

    def create_category(self, name: str):
        """
        Raises:
            AppException(ErrorCode.RESOURCE_ALREADY_EXISTS)
        """
        if (
            self.db_session.execute(
                select(Category).where(Category.name == name)
            ).scalar_one_or_none()
            is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Category already exists"
            )
        category = Category(name=name)
        self.db_session.add(category)

    def rename_category(self, category_id: int, new_name: str):
        """

        Raises:
            AppException(ErrorCode.RESOURCE_NOT_FOUND)
            AppException(ErrorCode.RESOURCE_ALREADY_EXISTS)

        """
        category = self.db_session.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        if category is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category does not exist")
        if (
            self.db_session.execute(
                select(Category).where(Category.name == new_name)
            ).scalar_one_or_none()
            is not None
        ):
            raise AppException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "Category already exists"
            )
        category.name = new_name
        self.db_session.add(category)

    def delete_category(self, category_id: int):
        """
        Raises:
            AppException(ErrorCode.RESOURCE_NOT_FOUND)
            AppException(ErrorCode.RESOURCE_IN_USE)
        """
        category = self.db_session.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()

        if category is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Category does not exist")

        is_used = self.db_session.execute(
            select(Document).where(Document.category_id == category_id).limit(1)
        ).scalar_one_or_none()

        if is_used:
            raise AppException(ErrorCode.RESOURCE_IN_USE, "Category is in use")

        self.db_session.delete(category)


def get_category_service(db_session: DBSessionDep):
    return CategoryService(db_session=db_session)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
