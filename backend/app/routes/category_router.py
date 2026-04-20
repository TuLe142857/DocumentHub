from fastapi import APIRouter

from app.core import APIResponse, ResponseSuccessSchema
from app.schemas.category_schema import CategorySchema
from app.services.category_service import CategoryServiceDep

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=ResponseSuccessSchema[list[CategorySchema]])
def get_available_categories(category_service: CategoryServiceDep):
    categories = category_service.list_all_categories()
    res = [CategorySchema.model_validate(c) for c in categories]
    return APIResponse.ok(data=res)
