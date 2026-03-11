import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


class DocumentLike(BaseModel):
    __tablename__ = "document_likes"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    document: Mapped["Document"] = relationship(backref="liked_by")
    liked_by: Mapped["User"] = relationship(backref="liked_documents")
