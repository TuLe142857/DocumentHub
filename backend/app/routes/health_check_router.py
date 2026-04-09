from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("", response_model=ResponseSuccessSchema)
def health_check():
    return APIResponse.ok()
