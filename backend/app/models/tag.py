from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class Tag(BaseModel):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    documents: Mapped[List["Document"]] = relationship(
        secondary="document_tags", back_populates="tags"
    )


__document_tags_table__ = Table(
    "document_tags",
    BaseModel.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
