import datetime
import enum
from typing import List

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from .base import ORMBase


class DocumentVisibility(enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class DocumentStatus(enum.Enum):
    # document is uploading, calc checksum, conver PDF for preview
    PROCESSING = "PROCESSING"

    # document ready for select
    READY = "READY"

    # document deleted by owner(soft delete)
    DELETED = "DELETED"

    # banned
    BANNED = "BANNED"


class Document(ORMBase):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    visibility: Mapped[DocumentVisibility] = mapped_column(
        Enum(DocumentVisibility), server_default=DocumentVisibility.PUBLIC.value
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), server_default=DocumentStatus.PROCESSING.value
    )
    desc: Mapped[str | None] = mapped_column(Text)
    file_type: Mapped[str] = mapped_column(String(10))
    thumbnail_object_key: Mapped[str] = mapped_column(String(100))
    file_object_key: Mapped[str] = mapped_column(String(128))
    file_preview_object_key: Mapped[str] = mapped_column(String(128))
    sha256sum: Mapped[str | None] = mapped_column(String(256))
    md5sum: Mapped[str | None] = mapped_column(String(128))
    page_count: Mapped[int] = mapped_column(server_default="0")
    view_count: Mapped[int] = mapped_column(server_default="0")
    like_count: Mapped[int] = mapped_column(server_default="0")
    download_count: Mapped[int] = mapped_column(server_default="0")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )

    # deleted by user
    # auto delete after 30 days
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)

    # banned by admin
    # auto delete after ~ 30 days
    # banned_at != null when status == "BANNED"
    banned_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)

    owner: Mapped["User"] = relationship(back_populates="documents")
    liked_by: Mapped[List["DocumentLike"]] = relationship(back_populates="document")
    category: Mapped["Category"] = relationship(back_populates="documents")
    tags: Mapped[List["Tag"]] = relationship(
        secondary="document_tags", back_populates="documents"
    )
    collection_items: Mapped[List["CollectionItem"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    reports: Mapped[list["DocumentReport"]] = relationship(back_populates="document")

    __table_args__ = (
        UniqueConstraint("owner_id", "title", name="unique_document_title"),
    )


class Category(ORMBase):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    documents: Mapped[List["Document"]] = relationship(back_populates="category")


class Tag(ORMBase):
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


document_tags_table = Table(
    "document_tags",
    ORMBase.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class DocumentLike(ORMBase):
    __tablename__ = "document_likes"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    document: Mapped["Document"] = relationship(back_populates="liked_by")
    user: Mapped["User"] = relationship(back_populates="liked_documents")
