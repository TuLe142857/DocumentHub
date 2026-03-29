from fastapi import APIRouter

from app.core import APIResponse, ResponsePaginationSchema, ResponseSuccessSchema

router = APIRouter(prefix="/dashboard")


@router.get("/stats", response_model=ResponseSuccessSchema)
def system_statistics():
    return APIResponse.ok()
