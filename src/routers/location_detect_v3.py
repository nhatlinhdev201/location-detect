import os
from fastapi import  APIRouter, HTTPException
import httpx
import json
import asyncio
from src.entities.main import Address_level
from src.models.location_detect_v3.execution.sync_data_mongo import process_api_data_location
from src.connects.database import mongo_db
from src.entities.main import AddressRequest
from src.models.location_detect_v3.execution.utils.mongo_execution import process_location
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor

load_dotenv()
COLLECTION_5 = os.getenv('COLLECTION_5')
API_DATA = os.getenv('API_DATA')
BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
max_workers = int(os.getenv('MAX_WORKER')) 


router = APIRouter()

@router.get("/sync-data-location")
async def call_api_mongodb(): 
    url = f"{API_DATA}/api/ApiMain/API_spCallServer"
    headers = {"Content-Type": "application/json"}
    payload = {
        "Json": "",
        "func": "CPN_spLocationLevel",
        "API_key": "netcoApikey2025"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data_str = response.text.replace("\\/", "/")
            data_listtmp = json.loads(data_str)
            data_list = json.loads(data_listtmp)


            if isinstance(data_list, list):
                # addresses = [Address(**item) for item in data_list]
                addresses = []
                for item in data_list:
                    # Kiểm tra xem các trường bắt buộc có tồn tại và không phải là null
                    if all(field in item and item[field] is not None for field in['id', 'name', 'code_local', 'type', 'parent_id']):
                        addresses.append(Address_level(**item))
                
                processed_data = process_api_data_location(addresses)  
                if processed_data:
                    collection = await mongo_db.get_collection(COLLECTION_5)
                    await collection.delete_many({})
                    await collection.insert_many(processed_data)
                    return {"message": "Success"}
                else:
                    raise HTTPException(status_code=500, detail="No processed data available")
            else:
                raise HTTPException(status_code=500, detail="Invalid data format: Expected a list")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"JSON decode error: {str(e)}")
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
# @router.post('/locations')
# async def analyze_multiple_locations(request: AddressRequest):
#     if not request.locations:
#         raise HTTPException(status_code=400, detail="Input không hợp lệ")

#     batch_size = BATCH_SIZE
#     results = []

#     for i in range(0, len(request.locations), batch_size):
#         batch = request.locations[i:i + batch_size]
        
#         tasks = [process_location(i + index, user_input) for index, user_input in enumerate(batch)]
        
#         batch_results = await asyncio.gather(*tasks)
        
#         results.extend(batch_results)
    
#     return results

# @router.post('/locations')
# async def analyze_multiple_locations(request: AddressRequest):
#     if not request.locations:
#         raise HTTPException(status_code=400, detail="Input không hợp lệ")

#     results = []
#     loop = asyncio.get_event_loop()
#     max_workers = min(32, len(request.locations))  # Giới hạn số tiến trình tối đa theo số lượng địa chỉ

#     with ProcessPoolExecutor(max_workers=max_workers) as executor:
#         # Chia các địa chỉ thành các batch
#         for i in range(0, len(request.locations), BATCH_SIZE):
#             batch = request.locations[i:i + BATCH_SIZE]
#             tasks = [
#                 loop.run_in_executor(executor, process_location_sync, index, user_input)
#                 for index, user_input in enumerate(batch)
#             ]
#             batch_results = await asyncio.gather(*tasks)
#             results.extend(batch_results)

#     return results

# def process_location_sync(index, user_input):
#     # Chuyển đổi bất đồng bộ sang đồng bộ
#     loop = asyncio.get_event_loop()
#     return loop.run_until_complete(process_location(index, user_input))


@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    results = []
    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        tasks = [
            loop.run_in_executor(executor, process_location_sync, index, user_input)
            for index, user_input in enumerate(request.locations)
        ]
        results = await asyncio.gather(*tasks)

    return results

def process_location_sync(index, user_input):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(process_location(index, user_input))