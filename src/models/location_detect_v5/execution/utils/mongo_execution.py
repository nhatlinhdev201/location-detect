from src.models.location_detect_v3.execution.search_utils import find_best
from src.models.location_detect_v3.execution.format_data_utils import format_address, check_phone_number
from src.connects.database import mongo_db
from src.connects.caching import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_3 = os.getenv('COLLECTION_3')

replacements = [
    {"key": " phuong ", "value": " "},
    {"key": " quan ", "value": " "},
    {"key": " huyen ", "value": " "},
    {"key": " xa ", "value": " "},
    {"key": " tinh ", "value": " "},
]

async def process_location(index, user_input): 

    formatted_input = format_address(user_input)

    # Tạo key cho cache
    cache_key = f"location:{formatted_input}"

    # Kiểm tra xem dữ liệu có trong cache không
    if cache_key in lru_cache:
        return {
            'index': index,
            'data': lru_cache[cache_key]  
        }
    # Kiểm tra dữ liệu đầu vào
    if not user_input:
        return {
            'index': index,
            'data': {
                'error': "Input không hợp lệ",
                'address': user_input
            }
        }

    if check_phone_number(user_input):
        input_keywords = formatted_input.split()
        
        # Truy vấn vào MongoDB
        collection = await mongo_db.get_collection(COLLECTION_3)

        query = {
            "$or": [
                {"city_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
                {"district_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
                {"ward_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}}
            ]
        }

        results = await collection.find(query).to_list(length=None)

        best_match = await find_best(formatted_input, results, user_input)

        if best_match['score'] == 3 or (best_match['ward_score'] == 1 and best_match['city_score'] == 1):
            # Lưu kết quả vào cache
            lru_cache[cache_key] = best_match if best_match else "Không tìm thấy kết quả"

        return {
            'index': index,  
            'data': best_match if best_match else "Không tìm thấy kết quả"
        }
    else:
        return {
            'index': index,  
            'data': {
                'error': "Vui lòng không để số điện thoại trong vị trí!",
                'address': user_input
            }
        }
    
    
async def query_data(user_input):
    
    formatted_input = format_address(user_input)

    formatted_input_tmp = formatted_input 

    input_keywords = formatted_input_tmp.split()

    collection = await mongo_db.get_collection(COLLECTION_3) 

    query = {
        "$or": [
            {"city_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
            {"district_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
            {"ward_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}}
        ]
    }
    results = await collection.find(query).to_list(length=None)
    
    return results
