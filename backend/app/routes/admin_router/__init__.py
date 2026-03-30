from fastapi import APIRouter

from .category import router as category_router
from .documents import router as document_router
from .report import router as report_router
from .user import router as user_router

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

admin_router.include_router(report_router)
admin_router.include_router(document_router)
admin_router.include_router(user_router)
admin_router.include_router(category_router)
