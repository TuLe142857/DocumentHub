from fastapi import APIRouter

from app.core import APIResponse, ResponsePaginationSchema
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.search_schema import SearchQueryDep
from app.services.jwt_service import OptionalAccessToken

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=ResponsePaginationSchema[DocumentSummaryResponse])
def search(
    access_token: OptionalAccessToken,
    query: SearchQueryDep,
):
    return APIResponse.paginate(
        current_page=query.page, per_page=query.limit, total_items=0, data=[]
    )
