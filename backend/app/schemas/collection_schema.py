from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.core import PaginationQuery


class CollectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: Annotated[int, Field()]
    name: Annotated[str, Field()]
    total_items: Annotated[
        int, Field(validation_alias="items"), BeforeValidator(lambda _: len(_))
    ]


class CollectionQuery(PaginationQuery):
    model_config = ConfigDict(extra="forbid")
    q: Annotated[
        str | None, Field(default=None, description="Search query, default None")
    ]
    document_id: Annotated[
        int | None,
        Field(
            default=None,
            description="Collection must contain specific document id. Default None(ignored)",
        ),
    ]


class CollectionItemQuery(PaginationQuery):
    model_config = ConfigDict(extra="forbid")
    q: Annotated[
        str | None, Field(default=None, description="Search query, default None")
    ]
