from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.get("/whoami")
def whoami():
    pass


@router.post("/register")
def request_registration():
    pass
