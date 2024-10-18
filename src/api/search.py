from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from src.utils.search_utils import find_best_matches
from src.utils import format_address

router = APIRouter()

# Đọc dữ liệu từ file JSON
with open('src/data/json_data_location_level3.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

class SearchRequest(BaseModel):
    input: str

@router.post('/')
async def search(request: SearchRequest):
    user_input = request.input
    if not user_input:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    # Tiền xử lý input
    formatted_input = format_address(user_input)

    # Tìm kiếm và lấy kết quả
    best_matches = find_best_matches(formatted_input, data)

    return best_matches

@router.get('/locations')
async def search_location(q: str = None):
    user_input = q
    if not user_input:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    # Tiền xử lý input
    formatted_input = format_address(user_input)

    # Tìm kiếm và lấy kết quả
    best_matches = find_best_matches(formatted_input, data)

    return best_matches
