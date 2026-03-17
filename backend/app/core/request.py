from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: Annotated[int, Field(ge=0, description="Page number")]
    limit: Annotated[int, Field(ge=0, description="Maximum number of items per page")]


def get_pagination_params(
    page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(10, ge=1, le=100, description="Max items per page"),
):
    return PaginationParams(page=page, limit=limit)


PaginationParamsDep = Annotated[PaginationParams, Depends(get_pagination_params)]
