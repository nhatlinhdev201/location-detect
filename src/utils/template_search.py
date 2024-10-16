import json
from src.utils.format_data_utils import format_address

def preprocess_input(user_input):
    """Chuẩn hóa input người dùng bằng cách sử dụng hàm format_address."""
    user_input = format_address(user_input)
    return user_input

def calculate_score(user_input, keys):
    """Tính điểm cho mỗi địa chỉ dựa trên input và keys."""
    score = 0
    for key in keys:
        if key in user_input:
            score += 1
            user_input = user_input.replace(key, '')  # Xóa key khỏi input
    return score

def find_best_matches(user_input, data):
    """Tìm kiếm các địa chỉ tốt nhất dựa trên input của người dùng."""
    results = []

    for entry in data:
        score = calculate_score(user_input, entry['keys'])
        if score > 0:
            results.append({
                'city': entry['city'],
                'city_id': entry['city_id'],
                'district': entry['district'],
                'district_id': entry['district_id'],
                'ward': entry['ward'],
                'ward_id': entry['ward_id'],
                'score': score
            })

    # Sắp xếp kết quả theo điểm
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]  # Chỉ trả về top 5 kết quả

# Đọc dữ liệu từ file JSON
with open('data/DataLocation.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Nhập input từ người dùng
user_input = input("Nhập vào địa chỉ bạn muốn tìm kiếm: ")

# Tiền xử lý input
formatted_input = preprocess_input(user_input)

# Tìm kiếm và lấy kết quả
best_matches = find_best_matches(formatted_input, data)

# In ra kết quả
print("\nTop 5 địa chỉ phù hợp nhất:")
for match in best_matches:
    print(f"Địa chỉ: {match}, Điểm: {match['score']}")