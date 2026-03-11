from fastapi import APIRouter

from app.core import APIResponse, ResponseErrorSchema, ResponseSuccessSchema

router = APIRouter(prefix="/health")


@router.get("/", response_model=ResponseSuccessSchema[None])
def health_check():
    return APIResponse.ok()
