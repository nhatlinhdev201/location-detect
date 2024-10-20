from fastapi import APIRouter, HTTPException
import json
from src.utils.search_utils import find_best, find_best_matches
from src.utils.format_data_utils import format_address
from typing import List
from pydantic import BaseModel

class AddressRequest(BaseModel):
    locations: List[str]

class SearchRequest(BaseModel):
    input: str

router = APIRouter()

# Đọc dữ liệu từ file JSON
with open('src/data/json_data_location.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

@router.get('/locations')
async def search_location(q: str = None):
    user_input = q
    if not user_input:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    # Tiền xử lý input
    formatted_input = format_address(user_input)

    # Tìm kiếm và lấy kết quả
    best_matches = find_best_matches(formatted_input, data, user_input)

    return best_matches


@router.post('/locations-all')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    results = []

    for index, user_input in enumerate(request.locations):
        formatted_input = format_address(user_input)  
        best_match = find_best(formatted_input, data, user_input) 

        results.append({
            'index': index,
            'data': best_match if best_match else "Không tìm thấy kết quả"
        })

    return results