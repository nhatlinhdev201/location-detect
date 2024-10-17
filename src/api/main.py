from fastapi import APIRouter
from src.api.search import router as search_router
# from src.api.other import router as other_router

api_router = APIRouter()
api_router.include_router(search_router, prefix="/search")
# other_router.include_router(other_router)