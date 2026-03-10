from sqlalchemy import ForeignKey, DateTime, func
import datetime
from .base_model import BaseModel

from sqlalchemy.orm import relationship, Mapped, mapped_column


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
