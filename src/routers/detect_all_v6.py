import asyncio
from fastapi import HTTPException, APIRouter
from src.connects.database import mongo_db
from dotenv import load_dotenv
import os
from src.entities.main import AddressRequest
from src.routers.detect_all_v5 import get_data_from_collection, process_location

load_dotenv()
COLLECTION_35 = os.getenv('COLLECTION_35')
max_workers = int(os.getenv('MAX_WORKER')) 

router = APIRouter()


async def analyze_location(user_input, collection):
    collection_data = await get_data_from_collection(user_input, collection)
    result = await process_location(user_input, collection_data)
    return result

@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")
    
    collection = await mongo_db.get_collection(COLLECTION_35)

    # Giới hạn số lượng yêu cầu đồng thời
    semaphore = asyncio.Semaphore(10)  

    async def bounded_analyze_location(user_input):
        async with semaphore:
            return await analyze_location(user_input, collection)

    # Chạy tất cả các địa chỉ cùng một lúc
    tasks = [bounded_analyze_location(user_input) for user_input in request.locations]
    raw_results = await asyncio.gather(*tasks)

    indexed_results = [
        {'index': index, 'data': result['data']}
        for index, result in enumerate(raw_results)
    ]

    return indexed_results