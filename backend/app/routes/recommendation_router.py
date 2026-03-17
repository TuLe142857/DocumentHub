from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.recommendation_schema import SimilarQueryDep, TrendingQueryDep
from app.services.jwt_service import OptionalAccessToken

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])


@router.get(
    "/for_me", response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]]
)
def get_personalized_recommendation(access_token: OptionalAccessToken):
    return APIResponse.ok([])


@router.get(
    "/trending", response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]]
)
def recommend_trending(access_token: OptionalAccessToken, query: TrendingQueryDep):
    return APIResponse.ok([])


@router.get(
    "/similar/{document_id}",
    response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]],
)
def recommend_similar(
    document_id: int, access_token: OptionalAccessToken, query: SimilarQueryDep
):
    return APIResponse.ok([])
