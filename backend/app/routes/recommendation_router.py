from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.core.sercurity.jwt import OptionalAccessToken
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.recommendation_schema import SimilarQueryDep, TrendingQueryDep

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])
from app.services.recommendation_service import RecommendationServiceDep


@router.get(
    "/for_me", response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]]
)
def get_personalized_recommendation(access_token: OptionalAccessToken):
    return APIResponse.ok([])


@router.get(
    "/trending", response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]]
)
def recommend_trending(
    access_token: OptionalAccessToken,
    query: TrendingQueryDep,
    recommender: RecommendationServiceDep,
):
    doc_list = recommender.get_trending(
        category_id=query.category_id, timeframe=query.timeframe, limit=query.limit
    )

    res_data = [DocumentSummaryResponse.model_validate(doc) for doc in doc_list]
    return APIResponse.ok(res_data)


@router.get(
    "/similar/{document_id}",
    response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]],
)
def recommend_similar(
    document_id: int, access_token: OptionalAccessToken, query: SimilarQueryDep
):
    return APIResponse.ok([])
