from fastapi import APIRouter, HTTPException
import os
import pandas as pd
import re
import unicodedata
from dotenv import load_dotenv
from src.connects.database import mongo_db
from src.entities.main import AddressRequest
from concurrent.futures import ProcessPoolExecutor
from src.connects.caching import lru_cache
import httpx
import json
import asyncio
from src.entities.main import Address_3
from src.connects.database import mongo_db
from src.entities.main import AddressRequest

load_dotenv()
COLLECTION_35 = os.getenv('COLLECTION_35')
max_workers = int(os.getenv('MAX_WORKER')) 

router = APIRouter()

# database
def extract_district_number_or_name(district_name):
    district_name = remove_accents(district_name)
    # Tách tên Quận và loại bỏ "Quận"
    number_or_name = district_name.replace("Quận", "").strip()
    # Trả về chuỗi số hoặc tên Quận
    return str(int(number_or_name)) if number_or_name.isdigit() else number_or_name

#Lấy lại chỉ số phường 
def extract_ward_number_or_name(ward_name):
    ward_name = remove_accents(ward_name)
    # Tách tên phường và loại bỏ "Phường"
    number_or_name = ward_name.replace("Phường", "").strip()
    # Trả về chuỗi số nếu là số, ngược lại trả về tên phường
    return str(int(number_or_name)) if number_or_name.isdigit() else number_or_name

def process_api_data(data_list):

    # Kiểm tra kiểu dữ liệu của data_list
    if not isinstance(data_list, list):
        raise ValueError("data_list phải là một danh sách")
    
    data_list = [
    {
        "city_id": addr.city_id,
        "city_name": addr.city_name,
        "district_id": addr.district_id,
        "district_name": addr.district_name,
        "ward_id": addr.ward_id,
        "ward_name": addr.ward_name,
    }
    for addr in data_list
]

    if not all(isinstance(item, dict) for item in data_list):
        raise ValueError("Mỗi phần tử trong data_list phải là một từ điển")

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data_list)

    required_columns = ['city_name', 'city_id', 'district_name', 'district_id', 'ward_name', 'ward_id']
    
    for column in required_columns:
        if column not in df.columns:
            df[column] = None  

    # Lọc các cột cần thiết
    df_filtered = df[required_columns].copy()

    # Xóa bản sao và tạo bản sao mới
    df_unique = df_filtered.drop_duplicates().copy() 

    # Đồng bộ hóa định dạng dữ liệu
    df_unique['district_name'] = df_unique['district_name'].apply(
        lambda x: f"Quận {int(x)}" if str(x).isdigit() else f"Quận {int(x.strip())}" if x.strip().isdigit() else x.strip()
    )
    df_unique['ward_name'] = df_unique['ward_name'].apply(
        lambda x: f"Phường {int(x)}" if str(x).isdigit() else f"Phường {int(x.strip())}" if x.strip().isdigit() else x.strip()
    )

    # Tạo cột keys
    df_unique['district_nomal'] = df_unique['district_name'].apply(extract_district_number_or_name)
    df_unique['ward_nomal'] = df_unique['ward_name'].apply(extract_ward_number_or_name)
    df_unique['city_nomal'] = df_unique['city_name'].apply(lambda x: remove_accents(x))

    df_unique['keys'] = df_unique.apply(lambda row: [row['city_nomal'].replace(" ", ""),row['district_nomal'].replace(" ", ""),row['ward_nomal'].replace(" ", "")], axis=1)

    # Chuyển đổi thành định dạng json
    json_data = df_unique[['city_name', 'district_name', 'ward_name', 'district_id', 'ward_id', 'city_id','keys', 'city_nomal', 'district_nomal', 'ward_nomal']].to_dict(orient='records')

    return json_data



@router.get("/sync-data-mongodb")
async def call_api_mongodb(): 
    # url = "http://api-v4-erp.chuyenphatnhanh.vn/api/ApiMain/API_spCallServer"
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
                
                processed_data = process_api_data(addresses)  
                if processed_data:
                    collection = await mongo_db.get_collection(COLLECTION_35)
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

# end database

# Xử lý input

# Biến chuẩn hóa
replacements = [
    {"key": " p.", "value": " phuong "},
    {"key": " p ", "value": " phuong "},
    {"key": " h ", "value": " "},
    {"key": " h.", "value": " "},
    {"key": " q ", "value": " quan "},
    {"key": " q.", "value": " quan "},
    {"key": " tx ", "value": " "},
    {"key": " tx.", "value": " "},
    {"key": " tp ", "value": " "},
    {"key": " tp.", "value": " "},
    {"key": " hcm", "value": " ho chi minh "},
    {"key": " tphcm", "value": " ho chi minh "},
    {"key": " thanh pho ", "value": " "},
    {"key": " hn ", "value": " ha noi "}
]

delimiters_ward = [" phuong", " p.", " xa ", " x.", " khom "]
delimiters_city = [" tp ", " thanh pho ", " tp.", " tinh ", " t.", " t "]
delimiters_district = [" quan ", " q.", " huyen ", " h.", " tx"]

replacements_tmp = [
    {"key": " phuong ", "value": " "},
    {"key": " quan ", "value": " "},
    {"key": " huyen ", "value": " "},
    {"key": " xa ", "value": " "},
    {"key": " tinh ", "value": " "},
]

# Chức năng tạo pattern
def create_patterns(delimiters):
    return [rf"(.*?)\s*{re.escape(delimiter)}" for delimiter in delimiters]

patterns_ward = create_patterns(delimiters_ward)
patterns_district = create_patterns(delimiters_district)
patterns_city = create_patterns(delimiters_city)

def normalize_vn(text):
    return remove_accents(text.lower())

def format_number(text):
    text = re.sub(r'(phuong) 0([1-9])', r'\1 \2', text)

    text = re.sub(r'(quan) 0([1-9])', r'\1 \2', text)

    text = re.sub(r'p0?([1-9])', r'phuong \1', text)

    text = re.sub(r'q0?([1-9])', r'quan \1', text)

    text = re.sub(r'p([1-9])', r'phuong \1', text)   

    text = re.sub(r'q([1-9])', r'quan \1', text)   

    return text

def remove_accents(text):
    text = text.lower()
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd_form if not unicodedata.combining(c)).replace('đ', 'd')

def format_address(address):
    #1. Chuyển về viết thường và thay thế ác dấu , bằng khoảng trắng để tách từ
    address = remove_accents(address).replace(",", " ")

    #2. chuẩn hóa
    replacement_pattern = '|'.join(re.escape(r['key']) for r in replacements)
    address = re.sub(replacement_pattern, lambda m: next((r['value'] for r in replacements if r['key'] == m.group(0)), m.group(0)), address)

    #3. thay thế ký tự đặc biệt 
    address = re.sub(r'[\#\!\.\-]', ' ', address)

    #4. xử lý phường quận 0X
    address = format_number(address)

    # Bước 5: Bỏ đi các khoảng trắng thừa
    address = re.sub(r'\s+', ' ', address).strip()
    
    return f" {address} "

def contains_phone_number(input_string: str) -> bool:
    vietnam_phone_pattern = r'(?<!\d)(0[1-9]{1}[0-9]{8}|(?:\+84|84)[1-9]{1}[0-9]{8})(?!\d)'
    international_phone_pattern = r'(?<!\d)(\+?\d{1,3}[- ]?)?\d{10}(?!\d)'
    combined_pattern = f'({vietnam_phone_pattern})|({international_phone_pattern})'
    return re.search(combined_pattern, input_string)

def calculate_score(user_input, keys):
    
    input = format_address(user_input).replace(" ", "")
    score = {
        'ward': 0,
        'district': 0,
        'city': 0
    }

    # Kiểm tra từng key và cộng điểm cho loại tương ứng
    if len(keys) >= 3:  
        # Tìm và xóa lần xuất hiện cuối cùng của key[0] (thành phố)
        city_pos = input.rfind(keys[0])  
        if city_pos != -1:  # Nếu key[0] có trong input
            score['city'] = 1  # Cộng 1 điểm cho city
            input = input[:city_pos] + input[city_pos + len(keys[0]):] + " " 
        else:
            score['city'] = -0.5

        # Tìm và xóa lần xuất hiện cuối cùng của key[1] (huyện)
        district_pos = input.rfind(keys[1])  
        if district_pos != -1:  # Nếu key[1] có trong input
            score['district'] = 1  # Cộng 1 điểm cho district
            input = input[:district_pos] + input[district_pos + len(keys[1]):]+ " "  # Cắt bỏ key[1] chỉ lần cuối
        else:
            score['district'] = -0.3

        # Tìm và xóa lần xuất hiện cuối cùng của key[2] (phường)
        ward_pos = input.rfind(keys[2]) 
        if ward_pos != -1:  # Nếu key[2] có trong input
            score['ward'] = 1  # Cộng 1 điểm cho ward
            input = input[:ward_pos] + input[ward_pos + len(keys[2]):] + " "  # Cắt bỏ key[2] chỉ lần cuối
        else:
            score['ward'] = -0.1
        
    return score

async def extract_address(user_input, result): 
    user_input_tmp = remove_accents(user_input)

    if result['ward_score'] == 1 and result['city_score'] == 1:
        patterns = patterns_ward + [rf"(.*?)\s*{re.escape(normalize_vn(result['ward_name']))}"]
    elif result['district_score'] == 1 and result['city_score'] == 1 and result['ward_score'] != 1:
        patterns = patterns_district + [rf"(.*?)\s*{re.escape(normalize_vn(result['district_name']))}"]
    elif result['city_score'] == 1 and result['district_score'] != 1 and result['ward_score'] != 1:
        patterns = patterns_city + [rf"(.*?)\s*{re.escape(normalize_vn(result['city_name']))}"]
    else:
        return user_input

    for pattern in patterns:
        match = re.search(pattern, user_input_tmp, re.IGNORECASE)
        if match:
            delimiter_start = match.end(1)
            return user_input[:delimiter_start].strip().rstrip(",")
    
    return user_input

async def find_best(formatted_input, data, user_input):
    best_match = None
    highest_score = float('-inf')

    for entry in data:
        score = calculate_score(user_input, entry['keys'])
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

async def get_data_from_collection(user_input, collection):
    formatted_input = format_address(user_input)  
    formatted_input_tmp = formatted_input

    for replacement in replacements_tmp:
        key = replacement['key']
        value = replacement['value']
        formatted_input_tmp = formatted_input_tmp.replace(key, value)
    
    input_keywords = formatted_input_tmp.split()

    query = {
            "$or": [
                {"city_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
                {"district_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}},
                {"ward_nomal": {"$regex": "|".join(input_keywords), "$options": "i"}}
            ]
        }
    results = await collection.find(query).to_list(length=None)
    # print('call db---------',len(results))
    return results

async def process_location(user_input, collection_data):
    formatted_input = format_address(user_input).replace(" ", "")
    # cache_key = f"location:{formatted_input}"

    # if cache_key in lru_cache:
    #     return lru_cache[cache_key]

    if not user_input:
        return {'data': {'error': "Input không hợp lệ", 'address': user_input}}

    if contains_phone_number(user_input):
        return {'data': {'error': "Vui lòng không để số điện thoại trong vị trí !", 'address': user_input}}
    else:
        best_match = await find_best(formatted_input, collection_data, user_input)
        result = {'data': best_match if best_match else "Không tìm thấy kết quả"}

        # # Ghi vào cache nếu có kết quả phù hợp
        # if best_match and (best_match['score'] == 3 or (best_match['ward_score'] == 1 and best_match['city_score'] == 1)):
        #     lru_cache[cache_key] = result

        return result
        

def process_location_sync(user_input, collection_data):
    return asyncio.run(process_location(user_input, collection_data))

@router.post('/locations')
async def analyze_multiple_locations(request: AddressRequest):
    if not request.locations:
        raise HTTPException(status_code=400, detail="Input không hợp lệ")
    collection = await mongo_db.get_collection(COLLECTION_35)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, process_location_sync, user_input, await get_data_from_collection(user_input, collection))
            for user_input in request.locations
        ]
        raw_results = await asyncio.gather(*futures)

    indexed_results = [
        {'index': index, 'data': result['data']}
        for index, result in enumerate(raw_results)
    ]

    return indexed_results
