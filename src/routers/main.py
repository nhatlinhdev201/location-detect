from fastapi import APIRouter
from src.routers.location_detect import router as location_detect_router


router_detect = APIRouter()

router_detect.include_router(location_detect_router, prefix="/v1")

