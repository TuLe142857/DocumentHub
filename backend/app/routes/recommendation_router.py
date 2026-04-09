from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.recommendation_schema import SimilarQueryDep, TrendingQueryDep
from app.services.auth_service import OptionalCurrentUserDep
from app.services.recommendation_service import RecommendationServiceDep

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])


@router.get(
    "/for_me", response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]]
)
def get_personalized_recommendation(current_user: OptionalCurrentUserDep):
    return APIResponse.ok([])


@router.get(
    "/trending", response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]]
)
def recommend_trending(
    current_user: OptionalCurrentUserDep,
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
    document_id: int, current_user: OptionalCurrentUserDep, query: SimilarQueryDep
):
    return APIResponse.ok([])
