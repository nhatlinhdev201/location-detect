from fastapi import APIRouter
from src.api.search import router as search_router
# from src.api.test import router as test_router

api_router = APIRouter()
api_router.include_router(search_router, prefix="/search")
# test_router.include_router(test_router, prefix="/test")