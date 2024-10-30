from fastapi import  HTTPException, APIRouter
from src.connects.caching import lru_cache
from src.connects.database import mongo_db
from dotenv import load_dotenv
import os

load_dotenv()

CACHE_TIME = int(os.getenv('CACHE_TIME', 3600))  
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 3000)) 
CACHE_LOCATION = os.getenv('CACHE_LOCATION')

cache_router = APIRouter()

@cache_router.post("/clear")
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
    return lru_cache.items()

@cache_router.get("/info")
async def get_cache_info():
    return {
        "total_items": len(lru_cache),
        "max_size": lru_cache.maxsize,
        "remaining_space": lru_cache.maxsize - len(lru_cache)
    }

@cache_router.post("/backup")
async def backup_cache():
    collection = await mongo_db.get_collection(CACHE_LOCATION)

    # Xóa dữ liệu cũ trong collection để tránh trùng lặp
    collection.delete_many({})
    
    for key in lru_cache.keys():
        value = lru_cache[key]
        collection.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

    return {"message": "Backup cache vào MongoDB thành công.", "total_items": len(lru_cache)}

@cache_router.post("/restore")
async def restore_cache():
    collection = await mongo_db.get_collection(CACHE_LOCATION)

    # Xóa hết dữ liệu trong cache trước khi nạp lại
    lru_cache.clear()
    
    async for document in collection.find():
        key = document["key"]
        value = document["value"]
        lru_cache[key] = value

    return {"message": "Khôi phục cache từ MongoDB thành công.", "total_items": len(lru_cache)}