from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    """
    Base schema for pagination parameters.

    Provides default values for navigating paginated results.

    When serializing this model or its subclasses, prefer:
        model_dump(exclude_none=True)

    Avoid using:
        model_dump(exclude_unset=True)

    Using `exclude_unset=True` may omit the default values of "page" (1)
    and "limit" (10) from the output if they are not explicitly provided
    in the input.
    """

    page: Annotated[int, Field(ge=1, default=1, description="Page number")]
    limit: Annotated[
        int,
        Field(ge=1, le=100, default=10, description="Maximum number of items per page"),
    ]


PaginationQueryDep = Annotated[PaginationQuery, Query()]
