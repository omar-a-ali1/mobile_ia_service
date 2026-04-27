from fastapi import APIRouter
from numpy import rec

from src.routes.health_routes import router as health_router
from src.routes.camera_routes import router as camera_router
from src.routes.recognition_routes import router as recognition_router

router = APIRouter()

router.include_router(health_router)
router.include_router(recognition_router)
router.include_router(camera_router)