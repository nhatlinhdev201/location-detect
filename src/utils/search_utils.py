import json
import re
from src.utils.format_data_utils import format_address

def preprocess_input(user_input):
    """Chuẩn hóa input người dùng bằng cách sử dụng hàm format_address."""
    user_input = format_address(user_input)
    return user_input

def trim_whitespace(text):
    # Bước 1: Loại bỏ khoảng trắng thừa trước và sau chuỗi
    text = text.strip()
    
    # Bước 2: Thay thế khoảng trắng thừa giữa các từ thành một khoảng trắng duy nhất
    text = re.sub(r'\s+', ' ', text)
    
    return text

def calculate_score(user_input, keys):
    input = preprocess_input(user_input)
    
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
            input = input[:city_pos] + input[city_pos + len(keys[0]):] + " "  # Cắt bỏ key[0] chỉ lần cuối
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

def extract_address(user_input, delimiters, ward):
    
    """Cắt phần địa chỉ trước chuỗi ngăn cách từ user_input."""
    for delimiter in delimiters:
        # Tạo biểu thức regex để tìm phần địa chỉ trước delimiter
        pattern = rf"(.*?)(?=\s*{re.escape(delimiter)})"
        match = re.search(pattern, user_input)
        
        if match:
            return match.group(1).strip()  

    # Kiểm tra chuỗi P+số hoặc p+số đầu tiên
    pattern_p = r'(?i)(.*?)(?=\s*P[0-9]|\sp[0-9])' 
    match_p = re.search(pattern_p, user_input)
    
    if match_p:
        # Nếu tìm thấy P+số hoặc p+số, trả về phần trước P
        return match_p.group(1).strip()
    
    if ward != "":
        pattern = rf"(.*?)(?=\s*{re.escape(ward)})"
        match = re.search(pattern, user_input, re.IGNORECASE)  
    
        if match:
            return match.group(1).strip()
        
    return None
    
    
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
    
    delimiters = [" phuong ", " Phương ", "P.", "p.", "Phường ", "PHUONG ", "PHƯỜNG ",
                   " xa", " Xã ", " X.", " x.", " XA ", " XÃ ",
                   ]
    
    # Lọc qua top 5 results_tmp, cắt user_input lấy vị trí cụ thể là phần phía trước ward
    for result in results_tmp:
        if result['ward_score'] == 1:
            result['address'] = extract_address(user_input, delimiters, result['ward'])
        else:
            result['address'] = "chưa xác định"

    return results_tmp

def find_best(formatted_input, data, user_input):
    """Tìm kiếm địa chỉ tốt nhất dựa trên input của người dùng."""
    best_match = None
    highest_score = float('-inf')  # Khởi tạo điểm cao nhất với giá trị âm vô cực

    for entry in data:
        score = calculate_score(formatted_input, entry['keys'])
        total_score = sum(score.values())

        if total_score > highest_score:  # Chỉ lưu lại nếu điểm cao hơn
            highest_score = total_score
            best_match = {
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
            }

    if best_match:  # Nếu có kết quả tốt nhất
        delimiters = [" phuong ", " Phương ", "P.", "p.", "Phường ", "PHUONG ", "PHƯỜNG ",
                       " xa", " Xã ", " X.", " x.", " XA ", " XÃ "]
        
        if best_match['ward_score'] == 1:
            best_match['address'] = extract_address(user_input, delimiters, best_match['ward'])
        else:
            best_match['address'] = None

    return best_match