import os
from fastapi import FastAPI, APIRouter, HTTPException, Query
import httpx
import json
import asyncio
from src.entities.main import Address, Address_3
from src.models.location_detect_v2.execution.sync_data_mongo import process_api_data as process_api_data_mongo
from src.models.location_detect_v2.execution.sync_data_mongo_full import process_api_data_full as process_api_data_mongo_full
from src.models.location_detect_v2.execution.search_utils import find_best_matches
from src.models.location_detect_v2.execution.format_data_utils import format_address, check_phone_number
from src.connects.database import mongo_db
from src.entities.main import AddressRequest
from src.models.location_detect_v2.execution.utils.mongo_execution import process_location, query_data
from bson import ObjectId
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

COLLECTION_3 = os.getenv('COLLECTION_3')
COLLECTION_4 = os.getenv('COLLECTION_4')

router = APIRouter()

@router.post("/create_index_c4")
async def create_index():
    try:
        collection_4 = await mongo_db.get_collection(COLLECTION_4)
        index_name = await collection_4.create_index([("address", "text")], name="address_index")

        return {"message": "Index created", "index_name": index_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/create_index_c3")
async def create_index():
    try:
        collection_3 = await mongo_db.get_collection(COLLECTION_3)
        index_name =await collection_3.create_index([("city_nomal", 1), ("district_nomal", 1), ("ward_nomal", 1)], name="compound_location_index")
        return {"message": "Index created", "index_name": index_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/drop_index_c3")
async def drop_index():
    try:

        collection_3 = await mongo_db.get_collection(COLLECTION_3)
        await collection_3.drop_index("compound_location_index")

        return {"message": "Indexes dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/drop_index_c4")
async def drop_index():
    try:

        collection_4 = await mongo_db.get_collection(COLLECTION_4)
        await collection_4.drop_index("compound_location_index")

        return {"message": "Indexes dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/sync-data-mongodb-full")
async def call_api_mongodb_full():
    url = "http://api-v4-erp.chuyenphatnhanh.vn/api/ApiMain/API_spCallServer"
    headers = {"Content-Type": "application/json"}
    payload = {
        "Json": "",
        "func": "CPN_spLocationFullAddress",
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
                    if all(field in item and item[field] is not None for field in ['city_name', 'district_name', 'ward_name', 'district_id', 'ward_id', 'city_id', 'address', 'street_name']):
                        addresses.append(Address(**item))
                
                processed_data = process_api_data_mongo_full(addresses)  
                if processed_data:
                    collection = await mongo_db.get_collection(COLLECTION_4)
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

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_address(q: str = Query(..., min_length=1)):
    collection = await mongo_db.get_collection(COLLECTION_4)

    # Tìm kiếm địa chỉ chứa chuỗi người dùng nhập
    cursor = collection.find({"address": {"$regex": q, "$options": "i"}}).limit(5)
    results = []
    async for document in cursor:
        document["_id"] = str(document["_id"]) 
        results.append(document)  
    return results

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