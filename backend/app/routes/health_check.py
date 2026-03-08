from fastapi import APIRouter
from app.core import APIResponse, ResponseSuccessSchema, ResponseErrorSchema

router = APIRouter()


@router.get("/health", response_model=ResponseSuccessSchema[None])
def health_check():
    return APIResponse.ok()
