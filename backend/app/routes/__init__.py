from fastapi import APIRouter, FastAPI

from .admin_router import admin_router as admin_router
from .auth_router import router as auth_router
from .collection_router import router as collection_router
from .document_router import router as document_router
from .health_check_router import router as health_check_router
from .recommendation_router import router as recommendation_router
from .report_router import router as report_router
from .search_router import router as search_router
from .user_router import router as user_profile_router

api_router = APIRouter(prefix="/api")


api_router.include_router(admin_router)
api_router.include_router(health_check_router)
api_router.include_router(auth_router)
api_router.include_router(document_router)
api_router.include_router(collection_router)
api_router.include_router(recommendation_router)
api_router.include_router(report_router)
api_router.include_router(search_router)
api_router.include_router(user_profile_router)


def register_api_router(app: FastAPI):
    app.include_router(api_router)
