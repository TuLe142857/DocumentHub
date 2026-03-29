from .base import ORMBase
from .collections import Collection, CollectionItem
from .document import (
    Category,
    Document,
    DocumentLike,
    DocumentStatus,
    DocumentVisibility,
    Tag,
)
from .report import (
    DocumentReport,
    ModerationAction,
    ModerationLog,
    ReportReason,
    ReportStatus,
)
from .user import Gender, Role, User, UserProfile

try:
    from sqlalchemy.orm import configure_mappers

    configure_mappers()
except Exception as e:
    raise RuntimeError(f"ORM mapping validation failed: {e}")

__all__ = [
    "ORMBase",
    "Collection",
    "CollectionItem",
    "Category",
    "Document",
    "DocumentLike",
    "DocumentStatus",
    "DocumentVisibility",
    "Tag",
    "User",
    "UserProfile",
    "Gender",
    "Role",
    "DocumentReport",
    "ModerationAction",
    "ModerationLog",
    "ReportReason",
    "ReportStatus",
]
