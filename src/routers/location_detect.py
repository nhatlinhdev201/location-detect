from fastapi import APIRouter, HTTPException
import asyncio
import json
from src.entities.main import Address
from src.models.location_detect_v1.execution.search_utils import find_best, find_best_matches
from src.models.location_detect_v1.execution.format_data_utils import format_address, check_phone_number
from src.models.location_detect_v1.execution.format_to_json import import_data
from src.entities.main import AddressRequest

router = APIRouter()

# Đọc dữ liệu từ file JSON
with open('src/models/location_detect_v1/data/json_data_location.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

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

         # Tìm kiếm và lấy kết quả
         best_matches = find_best_matches(formatted_input, data, user_input)
    else:
        best_matches = [{'error': "Vui lòng không nhập số điện thoại trong địa chỉ !", 'address': user_input}]


    return best_matches


@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    results = []

    for index, user_input in enumerate(request.locations):
        if user_input is None or user_input == "":
            results.append({
                'index': index,
                'data': {
                    'error': "Input không hợp lệ",
                    'address': user_input
                }
            })
        elif check_phone_number(user_input):
            formatted_input = format_address(user_input)  
            best_match = find_best(formatted_input, data, user_input) 

            results.append({
                'index': index,
                'data': best_match if best_match else "Không tìm thấy địa chỉ !"
            })
        else:
            results.append({
                'index': index,
                'data': {
                    'error': "Vui lòng không để số điện thoại trong vị trí !",
                    'address': user_input
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
    if user_input is None or user_input == "":
        return {
            'index': index,
            'data': {
                'error': "Input không hợp lệ",
                'address': user_input
            }
        }
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
                'error': "Vui lòng không để số điện thoại trong vị trí !",
                'address': user_input

            }
        }

@router.post('/import-data')
async def handle_import_data():
    import_data()
    return "Success"
