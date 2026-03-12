from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["Document"])


@router.post("/")
def create_document():
    pass
