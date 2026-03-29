from fastapi import APIRouter

from app.core import APIResponse, ResponsePaginationSchema
from app.core.sercurity.jwt import OptionalAccessToken
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.search_schema import SearchQueryDep
from app.services.search_service import SearchServiceDep

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=ResponsePaginationSchema[DocumentSummaryResponse])
def search(
    access_token: OptionalAccessToken,
    query: SearchQueryDep,
    search_service: SearchServiceDep,
):
    if access_token:
        user_id = int(access_token.sub)
        docs, total_docs = search_service.search_documents_with_personalization(
            user_id=user_id,
            keywords=query.keywords,
            category_id=query.category_id,
            tags=query.tags,
            page=query.page,
            limit=query.limit,
        )
    else:
        docs, total_docs = search_service.search_documents(
            keywords=query.keywords,
            category_id=query.category_id,
            tags=query.tags,
            page=query.page,
            limit=query.limit,
        )
    res_data = [DocumentSummaryResponse.model_validate(doc) for doc in docs]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total_docs,
        data=res_data,
    )
