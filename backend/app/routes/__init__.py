from fastapi import APIRouter

from .auth_route import router as auth_router
from .collection_route import router as collection_router
from .document_route import router as document_router
from .health_check_route import router as health_check_router
from .recommendation_route import router as recommendation_router
from .search_route import router as search_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_check_router)
api_router.include_router(auth_router)
api_router.include_router(document_router)
api_router.include_router(collection_router)
api_router.include_router(recommendation_router)
api_router.include_router(search_router)
