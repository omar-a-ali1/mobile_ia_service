from fastapi import APIRouter
from ..controllers.health import health

router = APIRouter()

@router.get("/health")
def health_check():
    return health()
    