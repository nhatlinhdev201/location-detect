from src.models.location_detect_v2.execution.search_utils import find_best
from src.models.location_detect_v2.execution.format_data_utils import format_address, check_phone_number
from src.connects.database import mongo_db
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

    formatted_input_tmp = formatted_input

    for replacement in replacements:
        key = replacement['key']
        value = replacement['value']
        formatted_input_tmp = formatted_input_tmp.replace(key, value)


    if user_input is None or user_input == "":
        return {
            'index': index,
            'data': {
                'error': "Input không hợp lệ",
                'address': user_input
            }
        }
    if check_phone_number(user_input):
        input_keywords = formatted_input_tmp.split()

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
