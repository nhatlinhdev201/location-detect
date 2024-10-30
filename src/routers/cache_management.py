from fastapi import  HTTPException, APIRouter
from src.connects.caching import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

CACHE_TIME = int(os.getenv('CACHE_TIME', 3600))  
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 3000)) 

cache_router = APIRouter()

@cache_router.post("S/clear")
async def clear_cache():
    lru_cache.clear()
    return {"message": "Xóa thành công toàn bộ cache"}

@cache_router.delete("/item/{key}")
async def delete_cache_item(key: str):
    try:
        del lru_cache[key]
        return {"message": f"Key '{key}' đã xóa thành công"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Key '{key}' không tồn tại")

@cache_router.get("/items")
async def get_all_cache_items():
    return lru_cache.get_all()

@cache_router.get("/info")
async def get_cache_info():
    return {
        "total_items": len(lru_cache),
        "max_size": lru_cache.maxsize,
        "remaining_space": lru_cache.maxsize - len(lru_cache)
    }
