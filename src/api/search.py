from flask import request, jsonify
from . import api_blueprint  
from src.utils.search_utils import find_best_matches
from src.utils import format_address
import json

# Đọc dữ liệu từ file JSON
with open('src/data/DataLocation.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

@api_blueprint.route('/search', methods=['POST'])
def search():
    """API để tìm kiếm địa chỉ dựa trên input của người dùng."""
    user_input = request.json.get('input', '')
    if not user_input:
        return jsonify({"error": "Input không hợp lệ"}), 400

    # Tiền xử lý input
    formatted_input = format_address(user_input)

    # Tìm kiếm và lấy kết quả
    best_matches = find_best_matches(formatted_input, data)

    return jsonify(best_matches)
