from .base_model import BaseModel
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Category(BaseModel):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    documents: Mapped[List["Document"]] = relationship(back_populates="category")
