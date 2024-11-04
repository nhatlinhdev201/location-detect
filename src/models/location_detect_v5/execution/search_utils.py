import re
from src.models.location_detect_v5.execution.format_data_utils import remove_accents, format_address, nomalize_vn

delimiters_ward = [" phuong ", " p.", " xa ", " x.", " khom " ]
delimiters_city = [" tp ", " thanh pho ", " tp.", " tinh ", " t.", " t "]
delimiters_district = [" quan ", " q.", " huyen ", " h.", " tx"]

def create_patterns(delimiters):
    return [rf"(.*?)\s*{re.escape(delimiter)}" for delimiter in delimiters]

# Tạo patterns một lần cho từng loại địa điểm
patterns_ward = create_patterns(delimiters_ward)
patterns_district = create_patterns(delimiters_district)
patterns_city = create_patterns(delimiters_city)

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
    
async def find_best_matches(formatted_input, data, user_input):
    """Tìm kiếm các địa chỉ tốt nhất dựa trên input của người dùng."""
    results = []

    for entry in data:
        score = calculate_score(formatted_input, entry['keys'])
        total_score = sum(score.values())  

        if total_score > 0:
            results.append({
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
            })

    # Sắp xếp kết quả theo điểm tổng
    results.sort(key=lambda x: x['score'], reverse=True)
    results_tmp = results[:5]
    # Lọc qua top 5 results_tmp, cắt user_input lấy vị trí cụ thể là phần phía trước ward
    for result in results[:5]:
            result['address'] = await extract_address(user_input, result)

    return results_tmp

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

