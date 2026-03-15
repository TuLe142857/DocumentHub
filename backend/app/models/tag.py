from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from .base_model import BaseModel


class Tag(BaseModel):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    documents: Mapped[List["Document"]] = relationship(
        secondary="document_tags", back_populates="tags"
    )

    @staticmethod
    def get_or_create(
        name: str,
        session: Session,
    ) -> "Tag | None":
        with session.begin_nested():
            tag_in_db = session.execute(
                select(Tag).where(Tag.name == name)
            ).scalar_one_or_none()
            if tag_in_db is not None:
                return tag_in_db

            try:
                new_tag = Tag(name=name)
                session.add(new_tag)
                session.flush()
                return new_tag
            except IntegrityError:
                session.rollback()
                return session.execute(
                    select(Tag).where(Tag.name == name)
                ).scalar_one_or_none()


__document_tags_table__ = Table(
    "document_tags",
    BaseModel.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
