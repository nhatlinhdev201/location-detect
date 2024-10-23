# from fastapi import FastAPI, APIRouter, HTTPException
# import httpx
# import json
# from src.entities.main import Address  # Đảm bảo rằng đường dẫn này đúng
# from src.models.location_detect_v1.execution.sync_data import process_api_data  # Đảm bảo rằng đường dẫn này đúng
# from src.connects.redis_connect import redis_client
# from src.connects.curd import set_data, client

# router = APIRouter()

# @router.get("/sync-data")
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
#                 processed_data = process_api_data(addresses)

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
#         pipe.execute()  # Sử dụng await cho việc thực thi bất đồng bộ
#     except Exception as e:
#         print(f"Lỗi khi đẩy vào Redis: {e}")
