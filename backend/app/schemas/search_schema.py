from typing import Annotated

from fastapi import Query
from pydantic import Field

from app.core import PaginationQuery


class SearchQuery(PaginationQuery):
    """
    Schema for handling search and filtering queries with pagination support.

    This model extends PaginationQuery to include search-specific filters.

    IMPORTANT: To dump this model, use `.model_dump(exclude_none=True)`.
    Do NOT use `exclude_unset=True` because it will strip away critical
    pagination defaults (page=1, limit=10).
    """

    keywords: Annotated[str, Field()]
    category_id: Annotated[int | None, Field(default=None)]
    tags: Annotated[list[str], Field(default=[])]
    sort_by: Annotated[str | None, Field(default=None)]


SearchQueryDep = Annotated[SearchQuery, Query()]
