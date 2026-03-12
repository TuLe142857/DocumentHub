import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class Collection(BaseModel):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="collections")
    items: Mapped[List["CollectionItem"]] = relationship(back_populates="collection")

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="unique_collection_name"),
    )


class CollectionItem(BaseModel):
    __tablename__ = "collection_items"

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id"), primary_key=True
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), primary_key=True
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    collection: Mapped["Collection"] = relationship(back_populates="items")
    document: Mapped["Document"] = relationship(back_populates="collection_items")
