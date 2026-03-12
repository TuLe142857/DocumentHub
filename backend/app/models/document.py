import datetime
import enum
from typing import List

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class DocumentVisibility(enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class DocumentStatus(enum.Enum):
    # document is uploading, calc checksum, conver pdf for preview
    PROCESSING = "PROCESSING"

    # document ready for select
    READY = "READY"

    # banned
    BANNED = "BANNED"


class Document(BaseModel):
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
    file_object_key: Mapped[str] = mapped_column(String(128))
    file_preview_object_key: Mapped[str] = mapped_column(String(128))
    sha256sum: Mapped[str | None] = mapped_column(String(256))
    page_count: Mapped[int] = mapped_column()
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
        back_populates="document"
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "title", name="unique_document_title"),
    )
