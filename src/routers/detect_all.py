from fastapi import APIRouter, HTTPException
import os
import re
import unicodedata
from dotenv import load_dotenv
from src.connects.database import mongo_db
from src.entities.main import AddressRequest
from concurrent.futures import ProcessPoolExecutor
import asyncio
from src.connects.caching import lru_cache

load_dotenv()
COLLECTION_3 = os.getenv('COLLECTION_3')
max_workers = int(os.getenv('MAX_WORKER')) 
router = APIRouter()

replacements = [
    {"key": " p.", "value": " phuong "},
    {"key": " p ", "value": " phuong "},
    {"key": " h ", "value": " "},
    {"key": " q ", "value": " quan "},
    {"key": " q.", "value": " quan "},
    {"key": " tx ", "value": " "},
    {"key": " tp ", "value": " "},
    {"key": " hcm", "value": " ho chi minh "},
    {"key": " tphcm", "value": " ho chi minh "},
    {"key": " thanh pho ", "value": " "}
]

delimiters_ward = [" phuong ", " p.", " xa ", " x.", " khom " ]
delimiters_city = [" tp ", " thanh pho ", " tp.", " tinh ", " t.", " t "]
delimiters_district = [" quan ", " q.", " huyen ", " h.", " tx"]

def create_patterns(delimiters):
    return [rf"(.*?)\s*{re.escape(delimiter)}" for delimiter in delimiters]

patterns_ward = create_patterns(delimiters_ward)
patterns_district = create_patterns(delimiters_district)
patterns_city = create_patterns(delimiters_city)

def nomalize_vn(text):
    return remove_accents(text.lower())

def remove_accents(text):
    text = text.lower()
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd_form if not unicodedata.combining(c)).replace('đ', 'd')

def format_address(address):
    address = remove_accents(address).replace(",", " ")
    
    replacement_pattern = '|'.join(re.escape(r['key']) for r in replacements)
    address = re.sub(replacement_pattern, lambda m: next((r['value'] for r in replacements if r['key'] == m.group(0)), m.group(0)), address)
    
    address = re.sub(r'[\#\!\.\-]', ' ', address)
    address = re.sub(r'\s+', ' ', address).strip()
    
    return f" {address} "

def contains_phone_number(input_string: str) -> bool:
    vietnam_phone_pattern = r'(?<!\d)(0[1-9]{1}[0-9]{8}|(?:\+84|84)[1-9]{1}[0-9]{8})(?!\d)'
    international_phone_pattern = r'(?<!\d)(\+?\d{1,3}[- ]?)?\d{10}(?!\d)'
    combined_pattern = f'({vietnam_phone_pattern})|({international_phone_pattern})'
    return not re.search(combined_pattern, input_string)

def calculate_score(user_input, keys):
    input = format_address(user_input)
    
    # Điểm mặc định cho từng loại
    score_map = {
        'ward': {'score': 0, 'penalty': -0.1},
        'district': {'score': 0, 'penalty': -0.3},
        'city': {'score': 0, 'penalty': -0.5}
    }

    # Duyệt qua từng loại và cập nhật điểm
    for i, (key, type_name) in enumerate(zip(keys, score_map.keys())):
        pos = input.rfind(key)  # Tìm vị trí cuối cùng của key
        if pos != -1:
            score_map[type_name]['score'] = 1  # Cộng điểm
            input = input[:pos] + input[pos + len(key):] + " "  # Cắt bỏ key
        else:
            score_map[type_name]['score'] = score_map[type_name]['penalty']  # Cộng điểm âm nếu không tìm thấy

    return {k: v['score'] for k, v in score_map.items()}

async def extract_address(user_input, result): 
    user_input_tmp = remove_accents(user_input)

    if result['ward_score'] == 1 and result['city_score'] == 1:
        patterns = patterns_ward + [rf"(.*?)\s*{re.escape(nomalize_vn(result['ward_name']))}"]
    elif result['district_score'] == 1 and result['city_score'] == 1 and result['ward_score'] != 1:
        patterns = patterns_district + [rf"(.*?)\s*{re.escape(nomalize_vn(result['district_name']))}"]
    elif result['city_score'] == 1 and result['district_score'] != 1 and result['ward_score'] != 1:
        patterns = patterns_city + [rf"(.*?)\s*{re.escape(nomalize_vn(result['city_name']))}"]
    else:
        return user_input

    for pattern in patterns:
        match = re.search(pattern, user_input_tmp, re.IGNORECASE)  
        if match:
            delimiter_start = match.end(1)  
            return user_input[:delimiter_start].strip().rstrip(",")
    
    return user_input

async def find_best(formatted_input, data, user_input):
    """Tìm kiếm địa chỉ tốt nhất dựa trên input của người dùng."""
    best_match = None
    highest_score = float('-inf')  # Khởi tạo điểm cao nhất với giá trị âm vô cực

    for entry in data:
        score = calculate_score(formatted_input, entry['keys'])
        total_score = sum(score.values())

        if total_score > highest_score:  
            highest_score = total_score
            best_match = {
                'city_name': entry['city_name'],
                'city_id': entry['city_id'],
                'district_name': entry['district_name'],
                'district_id': entry['district_id'],
                'ward_name': entry['ward_name'],
                'ward_id': entry['ward_id'],
                'score': total_score,
                'ward_score': score['ward'],
                'district_score': score['district'],
                'city_score': score['city']
            }

    if best_match: 
            best_match['address'] = await extract_address(user_input, best_match)

    return best_match


async def get_data_from_collection(formatted_input, collection):
    input_keywords = formatted_input.split()
    query = {
        "$or": [
            {"city_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
            {"district_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
            {"ward_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}}
        ]
    }
    return await collection.find(query).to_list(length=None)

async def process_location(user_input, collection_data):
    formatted_input = format_address(user_input)

    # Kiểm tra cache
    cache_key = formatted_input
    if cache_key in lru_cache:
        return {'data': lru_cache[cache_key]}  # Trả kết quả từ cache

    if not user_input:
        return {'data': {'error': "Input không hợp lệ", 'address': user_input}}

    if contains_phone_number(user_input):
        best_match = await find_best(formatted_input, collection_data, user_input)
        result = {'data': best_match if best_match else "Không tìm thấy kết quả"}
        
        # Lưu vào cache
        if best_match['score'] == 3 or (best_match['ward_score'] == 1 and best_match['city_score'] == 1):
            lru_cache[cache_key] = result

        return result
    else:
        return {'data': {'error': "Vui lòng không để số điện thoại trong vị trí !", 'address': user_input}}
def process_location_sync(user_input, collection_data):
    # Chạy hàm process_location trong một bối cảnh đồng bộ
    return asyncio.run(process_location(user_input, collection_data))

@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")

    collection = await mongo_db.get_collection(COLLECTION_3)
    collection_data = await get_data_from_collection(format_address(request.locations[0]), collection)

    with ProcessPoolExecutor(max_workers=10) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, process_location_sync, user_input, collection_data)
            for user_input in request.locations
        ]
        raw_results = await asyncio.gather(*futures)

    # Thêm chỉ số vào kết quả
    indexed_results = [
        {'index': index, 'data': result['data']}
        for index, result in enumerate(raw_results)
    ]

    return indexed_results