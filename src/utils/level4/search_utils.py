import json
import re
from src.utils.format_data_utils import format_address

def preprocess_input(user_input):
    """Chuẩn hóa input người dùng bằng cách sử dụng hàm format_address."""
    user_input = format_address(user_input)
    return user_input

def calculate_score(user_input, keys):

    input = preprocess_input(user_input)
    """Tính điểm cho mỗi địa chỉ dựa trên input và keys, phân loại theo loại địa chỉ."""
    score = {
        'ward': 0,
        'district': 0,
        'city': 0
    }

    # Kiểm tra từng key và cộng điểm cho loại tương ứng
    if len(keys) >= 3:  
        # Tìm và xóa lần xuất hiện cuối cùng của key[2] trong input (tỉnh)
        city_pos = input.rfind(keys[0])  # Tìm lần xuất hiện cuối của 'city'
        if city_pos != -1:  # Nếu key[2] có trong input
            score['city'] += 1  # Cộng điểm cho city
            input = input[:city_pos] + input[city_pos + len(keys[2]):]  # Cắt bỏ key[2] chỉ lần cuối

        # Tìm và xóa lần xuất hiện cuối cùng của key[1] trong input (huyện)
        district_pos = input.rfind(keys[1])  # Tìm lần xuất hiện cuối của 'district'
        if district_pos != -1:  # Nếu key[1] có trong input
            score['district'] += 1  # Cộng điểm cho district
            input = input[:district_pos] + input[district_pos + len(keys[1]):]  # Cắt bỏ key[1] chỉ lần cuối
        
        # Tìm và xóa lần xuất hiện cuối cùng của key[0] trong input (phường)
        ward_pos = input.rfind(keys[2])  # Tìm lần xuất hiện cuối của 'ward'
        if ward_pos != -1:  # Nếu key[0] có trong input
            score['ward'] += 1  # Cộng điểm cho ward
            input = input[:ward_pos] + input[ward_pos + len(keys[0]):]  # Cắt bỏ key[0] chỉ lần cuối

    return score

def extract_address(user_input, delimiters):
    """Cắt phần địa chỉ trước chuỗi ngăn cách từ user_input."""
    for delimiter in delimiters:
        # Tạo biểu thức regex để tìm phần địa chỉ trước delimiter
        pattern = rf"(.*?)(?=\s*{re.escape(delimiter)})"
        match = re.search(pattern, user_input)
        
        if match:
            return match.group(1).strip()  

    return "chưa xác định"
    
def find_best_matches(formatted_input, data, user_input):
    """Tìm kiếm các địa chỉ tốt nhất dựa trên input của người dùng."""
    results = []

    for entry in data:
        score = calculate_score(formatted_input, entry['keys'])
        total_score = sum(score.values())  

        if total_score > 0:
            results.append({
                'city': entry['city'],
                'city_id': entry['city_id'],
                'district': entry['district'],
                'district_id': entry['district_id'],
                'ward': entry['ward'],
                'ward_id': entry['ward_id'],
                'score': total_score,
                'ward_score': score['ward'],
                'district_score': score['district'],
                'city_score': score['city']
            })

    # Sắp xếp kết quả theo điểm tổng
    results.sort(key=lambda x: x['score'], reverse=True)
    results_tmp = results[:5]
    
    delimiters = [" Phường ", " PHUONG ", " P."]
    
    # Lọc qua top 5 results_tmp, cắt user_input lấy vị trí cụ thể là phần phía trước ward
    for result in results_tmp:
        if result['ward_score'] == 1:
            result['address'] = extract_address(user_input, delimiters)
        else:
            result['address'] = "chưa xác định"

    return results_tmp

