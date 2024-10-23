from fastapi import APIRouter, HTTPException
import asyncio
import httpx
import json
from typing import List
from src.entities.main import Address
from src.models.location_detect_v1.execution.search_utils import find_best, find_best_matches
from src.models.location_detect_v1.execution.format_data_utils import format_address, check_phone_number
from src.models.location_detect_v1.execution.format_to_json import import_data
from src.entities.main import AddressRequest
from src.models.location_detect_v1.execution.sync_data import process_api_data
# from src.connects.database import mongo_db

router = APIRouter()

# Đọc dữ liệu từ file JSON
with open('src/models/location_detect_v1/data/json_data_location.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

@router.get('/location')
async def search_location(q: str = None):
    user_input = q
    if not user_input:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    if check_phone_number(user_input):
          # Tiền xử lý input
         formatted_input = format_address(user_input)    

         # Tìm kiếm và lấy kết quả
         best_matches = find_best_matches(formatted_input, data, user_input)
    else:
        best_matches = [{'error': "Vui lòng không nhập số điện thoại trong địa chỉ !"}]


    return best_matches


@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    results = []

    for index, user_input in enumerate(request.locations):
        if check_phone_number(user_input):
            formatted_input = format_address(user_input)  
            best_match = find_best(formatted_input, data, user_input) 

            results.append({
                'index': index,
                'data': best_match if best_match else "Không tìm thấy kết quả"
            })
        else:
            results.append({
                'index': index,
                'data': {
                    'error': "Vui lòng không để số điện thoại trong vị trí !"
                }
            })

    return results

@router.post('/location')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    results = await asyncio.gather(*(process_location(index, user_input) for index, user_input in enumerate(request.locations)))
    
    return results

async def process_location(index, user_input):
    if check_phone_number(user_input):
        formatted_input = format_address(user_input)  
        best_match = find_best(formatted_input, data, user_input) 
        return {
            'index': index,
            'data': best_match if best_match else "Không tìm thấy kết quả"
        }
    else:
        return {
            'index': index,
            'data': {
                'error': "Vui lòng không để số điện thoại trong vị trí !"
            }
        }

@router.post('/import-data')
async def handle_import_data():
    import_data()
    return "Success"

# @router.get("/sync-data")
# async def call_api():
#     url = "http://api-v4-erp.chuyenphatnhanh.vn/api/ApiMain/API_spCallServer"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "Json": "",
#         "func": "CPN_spLocationFullAddress",
#         "API_key": "netcoApikey2025"
#     }

#     async with httpx.AsyncClient(timeout = 60) as client:
#         response = await client.post(url, headers=headers, json=payload)

#     if response.status_code == 200:
#         try:
#             data_str = response.text
#             data_str = data_str.replace("\\/", "/")
#             data_listtmp = json.loads(data_str)
#             data_list = json.loads(data_listtmp)
#             if isinstance(data_list, list):
#                 # addresses = [Address(**item) for item in data_list]
#                 addresses = []
#                 for item in data_list:
#                     # Kiểm tra xem các trường bắt buộc có tồn tại và không phải là null
#                     if all(field in item and item[field] is not None for field in ['id', 'address', 'city_id', 'city_name', 'district_id', 'district_name', 'ward_id', 'ward_name', 'street_name', 'type_address']):
#                         addresses.append(Address(**item))
#                     else:
#                         print(f"Skipping item due to missing fields: {item}")
                
#                 processed_data = process_api_data(addresses)  
#                 if processed_data:
#                     collection = await mongo_db.get_collection("locations")
#                     await collection.delete_many({})
#                     await collection.insert_many(processed_data)
#                     return {"message": "Success"}
#                 else:
#                     raise HTTPException(status_code=500, detail="No processed data available")
#             else:
#                 raise HTTPException(status_code=500, detail="Invalid data format: Expected a list")
#         except json.JSONDecodeError as e:
#             raise HTTPException(status_code=500, detail=f"JSON decode error: {str(e)}")
#     else:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
