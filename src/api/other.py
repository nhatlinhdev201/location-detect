from flask import request, jsonify
from . import api_blueprint

@api_blueprint.route('/other', methods=['GET'])
def other_function():
    """Một API ví dụ khác."""
    return jsonify({"message": "Đây là một API khác!"})