from typing import Any, Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ORMBase

ModelType = TypeVar("ModelType", bound=ORMBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.db_session = db_session
        self.model: Type[ModelType] = model

    def _save(
        self,
        db_obj: ModelType,
        auto_flush: bool = True,
        auto_commit: bool = False,
        add_to_session: bool = True,
    ) -> ModelType:
        if add_to_session:
            self.db_session.add(db_obj)
        if auto_commit:
            self.db_session.commit()
            self.db_session.refresh(db_obj)
        elif auto_flush:
            self.db_session.flush()
            self.db_session.refresh(db_obj)
        return db_obj

    def get(
        self, ident: Any, *, on_not_found: Exception | None = None
    ) -> ModelType | None:
        """Retrieve a single record by its primary key.

        Args:
            ident: The primary key or composite key of the record.
            on_not_found: Optional exception to raise if the record is not found.

        Returns:
            The retrieved model instance, or None if not found and no exception is provided.

        Raises:
            Exception: The specified `on_not_found` exception if the record is missing.
        """
        db_obj = self.db_session.get(self.model, ident)
        if (
            (db_obj is None)
            and (on_not_found is not None)
            and (isinstance(on_not_found, Exception))
        ):
            raise on_not_found
        return db_obj

    def get_multi(
        self,
        *where,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
        filter_by: dict[str, Any] = None,
    ) -> tuple[Sequence[ModelType], int]:

        # Build base statement(not include pagination & order logic)
        stmt = select(self.model)
        if where:
            stmt = stmt.where(*where)
        if filter_by:
            stmt = stmt.filter_by(**filter_by)

        total_count = (
            self.db_session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()
            or 0
        )

        if total_count == 0:
            return [], 0

        if order_by is not None:
            if isinstance(order_by, (list, tuple)):
                stmt = stmt.order_by(*order_by)
            else:
                stmt = stmt.order_by(order_by)

        items = self.db_session.execute(stmt.offset(skip).limit(limit)).scalars().all()

        return items, total_count

    def create(
        self,
        obj: ModelType | CreateSchemaType | dict[str, Any],
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> ModelType:
        if isinstance(obj, self.model):
            db_obj = obj
        elif isinstance(obj, dict):
            db_obj = self.model(**obj)
        else:
            db_obj = self.model(**obj.model_dump())

        return self._save(db_obj, auto_flush=auto_flush, auto_commit=auto_commit)

    def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        *,
        auto_commit: bool = False,
        auto_flush: bool = True,
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude unset: remove unset field, any field was set=None still remain
            update_data = obj_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_obj, key, value)

        return self._save(db_obj, auto_flush=auto_flush, auto_commit=auto_commit)

    def delete(
        self, obj: ModelType, *, auto_commit: bool = False, auto_flush: bool = True
    ):
        self.db_session.delete(obj)
        if auto_commit:
            self.db_session.commit()
        elif auto_flush:
            self.db_session.flush()
