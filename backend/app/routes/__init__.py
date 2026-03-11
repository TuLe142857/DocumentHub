from fastapi import APIRouter

from .auth import router as auth_router
from .health_check import router as health_check_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_check_router)
api_router.include_router(auth_router)
