from .base import ORMBase

# from .category import Category
from .collections import Collection, CollectionItem
from .document import (
    Category,
    Document,
    DocumentLike,
    DocumentStatus,
    DocumentVisibility,
    Tag,
)

# from .like import DocumentLike
# from .tag import Tag, __document_tags_table__
from .user import Gender, Role, User, UserProfile

try:
    from sqlalchemy.orm import configure_mappers

    configure_mappers()
except Exception as e:
    raise RuntimeError(f"ORM mapping validation failed: {e}")
