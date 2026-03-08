from typing import List
from sqlalchemy import String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base_model import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    owner: Mapped["User"] = relationship(back_populates="documents")
    category: Mapped["Category"] = relationship(back_populates="documents")
    tags: Mapped[List["Tag"]] = relationship(
        secondary="document_tags", back_populates="documents"
    )
    collection_items: Mapped[List["CollectionItem"]] = relationship(
        back_populates="document"
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "title", name="unique_document_title"),
    )
