from typing import Annotated

from fastapi import APIRouter, Query

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.document_schema import DocumentSummarySchema
from app.schemas.recommendation_schema import TrendingQuery
from app.services.auth_service import OptionalCurrentUserDep
from app.services.recommendation_service import RecommendationServiceDep
from app.services.storage_service import StorageServiceDep

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])


@router.get(
    "/for_me", response_model=ResponseSuccessSchema[list[DocumentSummarySchema]]
)
def get_personalized_recommendation(current_user: OptionalCurrentUserDep):
    return APIResponse.ok(message="Coming Soon...")


@router.get(
    "/trending", response_model=ResponseSuccessSchema[list[DocumentSummarySchema]]
)
def recommend_trending(
    query: Annotated[TrendingQuery, Query()],
    recommender: RecommendationServiceDep,
    storage_service: StorageServiceDep,
):
    doc_list = recommender.get_trending(
        category_id=query.category_id, timeframe=query.timeframe, limit=query.limit
    )

    res_data = [
        DocumentSummarySchema.build(doc, storage_service.generate_document_url(doc)[0])
        for doc in doc_list
    ]
    return APIResponse.ok(res_data)


@router.get(
    "/similar/{document_id}",
    response_model=ResponseSuccessSchema[list[DocumentSummarySchema]],
)
def recommend_similar(
    document_id: int,
):
    return APIResponse.ok(message="Coming Soon...")
