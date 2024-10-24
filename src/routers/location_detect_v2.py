import os
from fastapi import FastAPI, APIRouter, HTTPException
import httpx
import json
import asyncio
from src.entities.main import Address, Address_3
from src.models.location_detect_v2.execution.sync_data_mongo import process_api_data as process_api_data_mongo
from src.models.location_detect_v2.execution.search_utils import find_best_matches
from src.models.location_detect_v2.execution.format_data_utils import format_address, check_phone_number
# from src.models.location_detect_v2.execution.sync_data_redis import process_api_data as process_api_data_redis
# from src.connects.redis_connect import redis_client
# from src.connects.curd import set_data, client
from src.connects.database import mongo_db
from src.entities.main import AddressRequest
from src.models.location_detect_v2.execution.utils.mongo_execution import process_location, query_data

from dotenv import load_dotenv

load_dotenv()

COLLECTION_3 = os.getenv('COLLECTION_3')

router = APIRouter()

# @router.get("/sync-data-redis")
# async def call_api():
#     url = "http://api-v4-erp.chuyenphatnhanh.vn/api/ApiMain/API_spCallServer"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "Json": "",
#         "func": "CPN_spLocationFullAddress",
#         "API_key": "netcoApikey2025"
#     }

#     async with httpx.AsyncClient(timeout=60) as client:
#         response = await client.post(url, headers=headers, json=payload)

#     if response.status_code == 200:
#         try:
#             data_str = response.text.replace("\\/", "/")
#             data_listtmp = json.loads(data_str)
#             data_list = json.loads(data_listtmp)

#             if isinstance(data_list, list):
#                 addresses = [
#                     Address(**item) for item in data_list
#                     if all(field in item and item[field] is not None for field in [
#                         'id', 'address', 'city_id', 'city_name',
#                         'district_id', 'district_name', 'ward_id',
#                         'ward_name', 'street_name', 'type_address'
#                     ])
#                 ]

#                 if not addresses:
#                     raise HTTPException(status_code=500, detail="No valid addresses found")

#                 # Định dạng lại dữ liệu
#                 processed_data = process_api_data_redis(addresses)

#                 if processed_data:
#                     await push_data_to_redis(processed_data)
#                     return {"message": "Success ok"}
#                 else:
#                     raise HTTPException(status_code=500, detail="No processed data available")
#             else:
#                 raise HTTPException(status_code=500, detail="Invalid data format: Expected a list")
#         except json.JSONDecodeError as e:
#             raise HTTPException(status_code=500, detail=f"JSON decode error: {str(e)}")
#     else:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

# async def push_data_to_redis(data_list):
#     # print(f"Đang đặt {data_list} dữ liệu với Redis")
#     # return 
#     """
#     Đẩy dữ liệu vào Redis.
#     """
#     pipe = redis_client.client.pipeline()  

#     for address in data_list:
#         redis_key = f"{address['id']}"  
#         print(f"Đang đặt Redis key: {redis_key} với giá trị: {address}")
#         client.set(redis_key, json.dumps(address))
#         # set_data()
#         # Chuyển đổi các giá trị không hợp lệ
#         # sanitized_address = {
#         #     key: (','.join(value) if isinstance(value, list) else str(value)) 
#         #     for key, value in address.items()
#         # }

#         # # Log để gỡ lỗi
#         # print(f"Đang đặt Redis key: {redis_key} với giá trị: {sanitized_address}")

#         # # Sử dụng HSET với các tham số riêng biệt
#         # for key, value in sanitized_address.items():
#         #     pipe.hset(redis_key, key, value)

#         # pipe.sadd("addresses", redis_key)  # Thêm vào một set
#         # print(f"Đang đặt Redis key: {redis_key} với giá trị: {sanitized_address}")

#     try:
#         pipe.execute()  
#     except Exception as e:
#         print(f"Lỗi khi đẩy vào Redis: {e}")


@router.get("/sync-data-mongodb")
async def call_api_mongodb():
    url = "http://api-v4-erp.chuyenphatnhanh.vn/api/ApiMain/API_spCallServer"
    headers = {"Content-Type": "application/json"}
    payload = {
        "Json": "",
        "func": "CPN_spLocationAddress",
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
                    if all(field in item and item[field] is not None for field in ['city_id', 'city_name', 'district_id', 'district_name', 'ward_id', 'ward_name']):
                        addresses.append(Address_3(**item))
                    else:
                        print(f"Skipping item due to missing fields: {item}")
                
                processed_data = process_api_data_mongo(addresses)  
                if processed_data:
                    collection = await mongo_db.get_collection(COLLECTION_3)
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


@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    batch_size = 50

    if not request.locations:
        raise HTTPException(status_code=400, detail="Không có địa chỉ hợp lệ")

    results = []
    for i in range(0, len(request.locations), batch_size):
        batch = request.locations[i:i + batch_size]
        batch_results = await asyncio.gather(
            *(process_location(index, user_input) for index, user_input in enumerate(batch))
        )
        results.extend(batch_results)
    
    return results

@router.get('/location')
async def search_location(q: str = None):
    user_input = q
    if not user_input:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")
    
    if user_input is None or user_input == "":
        best_matches = [{'error': "Input không hợp lệ"}]

    if check_phone_number(user_input):
        # Tiền xử lý input
        formatted_input = format_address(user_input)   

        data = await query_data(user_input)

        # Tìm kiếm và lấy kết quả
        best_matches = await find_best_matches(formatted_input, data, q)
    else:
        best_matches = [{'error': "Vui lòng không nhập số điện thoại trong địa chỉ !", 'address': user_input}]

    return best_matches