import json
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
    if len(keys) >= 3:  # Đảm bảo có đủ 3 phần
        if keys[0] in input:
            score['ward'] += 1
            input = input.replace(keys[0], '')

        if keys[1] in input:
            score['district'] += 1
            input = input.replace(keys[1], '')

        if keys[2] in input:
            score['city'] += 1
            input = input.replace(keys[2], '')

    return score

def find_best_matches(user_input, data):
    """Tìm kiếm các địa chỉ tốt nhất dựa trên input của người dùng."""
    results = []

    for entry in data:
        score = calculate_score(user_input, entry['keys'])
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
    return results[:5]
