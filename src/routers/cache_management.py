from fastapi import HTTPException, APIRouter
import redis.asyncio as redis  
from src.connects.database import mongo_db
from dotenv import load_dotenv
import os

load_dotenv()

# Cấu hình Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6378)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Kết nối đến Redis
redis_client = redis.from_url(
    f"redis://{REDIS_HOST}:{REDIS_PORT}",
    password='nhatlinhdev201',
    encoding="utf-8", 
    decode_responses=True
)

CACHE_LOCATION = os.getenv('CACHE_LOCATION')  # MongoDB collection name

cache_router = APIRouter()

# Xóa toàn bộ cache trong Redis
@cache_router.post("/clear")
async def clear_cache():
    # Dùng Redis command FLUSHDB để xóa toàn bộ dữ liệu trong database hiện tại
    await redis_client.flushdb()
    return {"message": "Xóa thành công toàn bộ cache"}

# Xóa một item cache theo key
@cache_router.delete("/item/{key}")
async def delete_cache_item(key: str):
    result = await redis_client.delete(key)
    if result == 0:
        raise HTTPException(status_code=404, detail=f"Key '{key}' không tồn tại trong cache")
    return {"message": f"Key '{key}' đã xóa thành công"}

# Lấy tất cả các item trong Redis
@cache_router.get("/items")
async def get_all_cache_items():
    # Lấy tất cả các key trong Redis
    keys = await redis_client.keys('*')
    items = {}
    for key in keys:
        items[key] = await redis_client.get(key)
    return items

# Lấy thông tin về cache (số lượng item, dung lượng tối đa...)
@cache_router.get("/info")
async def get_cache_info():
    # Redis không cung cấp trực tiếp thông tin dung lượng, chỉ có thể lấy số lượng key
    keys = await redis_client.keys('*')
    return {
        "total_items": len(keys),
    }

# Backup cache vào MongoDB
@cache_router.post("/backup")
async def backup_cache():
    collection = await mongo_db.get_collection(CACHE_LOCATION)

    # Xóa dữ liệu cũ trong collection để tránh trùng lặp
    collection.delete_many({})

    # Lấy tất cả các keys trong Redis và lưu vào MongoDB
    keys = await redis_client.keys('*')
    for key in keys:
        value = await redis_client.get(key)
        collection.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

    return {"message": "Backup cache vào MongoDB thành công.", "total_items": len(keys)}

# Restore cache từ MongoDB vào Redis
@cache_router.post("/restore")
async def restore_cache():
    collection = await mongo_db.get_collection(CACHE_LOCATION)

    # Xóa hết dữ liệu trong Redis trước khi nạp lại
    await redis_client.flushdb()

    # Lấy dữ liệu từ MongoDB và đưa vào Redis
    async for document in collection.find():
        key = document["key"]
        value = document["value"]
        await redis_client.set(key, value)

    return {"message": "Khôi phục cache từ MongoDB thành công."}
