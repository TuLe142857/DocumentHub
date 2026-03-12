from fastapi import APIRouter

from .auth import router as auth_router
from .collection import router as collection_router
from .document import router as document_router
from .health_check import router as health_check_router
from .recommendation import router as recommendation_router
from .search import router as search_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_check_router)
api_router.include_router(auth_router)
api_router.include_router(document_router)
api_router.include_router(collection_router)
api_router.include_router(recommendation_router)
api_router.include_router(search_router)
