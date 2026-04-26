from fastapi import APIRouter
from ..controllers.health import health

router = APIRouter()

@router.get("/")
def health_check():
    return health()
    