from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, Field


class TrendingQuery(BaseModel):
    category_id: Annotated[
        int | None,
        Field(
            ge=0,
            default=None,
            description="Optional category ID. If None or not provided, results will include items from all categories.",
        ),
    ]
    timeframe: Annotated[
        Literal["daily", "weekly", "monthly", "all_time"], Field(default="monthly")
    ]
    limit: Annotated[int, Field(ge=0, default=10)]


TrendingQueryDep = Annotated[TrendingQuery, Query()]


class SimilarQuery(BaseModel):
    limit: Annotated[int, Field(ge=0, default=10)]


SimilarQueryDep = Annotated[SimilarQuery, Query()]
