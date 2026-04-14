from typing import Annotated

from fastapi import APIRouter, Query

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.document_schema import DocumentSummaryResponse
from app.schemas.recommendation_schema import SimilarQuery, TrendingQuery
from app.services.auth_service import OptionalCurrentUserDep
from app.services.recommendation_service import RecommendationServiceDep
from app.services.storage_service import StorageServiceDep

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
    query: Annotated[TrendingQuery, Query()],
    recommender: RecommendationServiceDep,
    storage_service: StorageServiceDep,
):
    doc_list = recommender.get_trending(
        category_id=query.category_id, timeframe=query.timeframe, limit=query.limit
    )

    res_data = [
        DocumentSummaryResponse.build(
            doc, storage_service.generate_presigned_url_for_document(doc)[0]
        )
        for doc in doc_list
    ]
    return APIResponse.ok(res_data)


@router.get(
    "/similar/{document_id}",
    response_model=ResponseSuccessSchema[list[DocumentSummaryResponse]],
)
def recommend_similar(
    document_id: int,
    current_user: OptionalCurrentUserDep,
    query: Annotated[SimilarQuery, Query()],
):
    return APIResponse.ok([])
