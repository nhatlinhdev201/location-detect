# import re
# from src.models.location_detect_v1.execution.format_data_utils import remove_accents, format_address, nomalize_vn

# delimiters_ward = [" phuong ", " p.", " xa ", " x.", " khom " ]
# delimiters_city = [" tp ", " thanh pho ", " tp.", " tinh ", " t.", " t "]
# delimiters_district = [" quan ", " q.", " huyen ", " h.", " tx"]

# def preprocess_input(user_input):
#     """Chuẩn hóa input người dùng bằng cách sử dụng hàm format_address."""
#     user_input = format_address(user_input)
#     return user_input

# def trim_whitespace(text):
#     # Bước 1: Loại bỏ khoảng trắng thừa trước và sau chuỗi
#     text = text.strip()
    
#     # Bước 2: Thay thế khoảng trắng thừa giữa các từ thành một khoảng trắng duy nhất
#     text = re.sub(r'\s+', ' ', text)
    
#     return text

# def calculate_score(user_input, keys):
#     input = preprocess_input(user_input)
    
#     score = {
#         'ward': 0,
#         'district': 0,
#         'city': 0
#     }

#     # Kiểm tra từng key và cộng điểm cho loại tương ứng
#     if len(keys) >= 3:  
#         # Tìm và xóa lần xuất hiện cuối cùng của key[0] (thành phố)
#         city_pos = input.rfind(keys[0])  
#         if city_pos != -1:  # Nếu key[0] có trong input
#             score['city'] = 1  # Cộng 1 điểm cho city
#             input = input[:city_pos] + input[city_pos + len(keys[0]):] + " "  # Cắt bỏ key[0] chỉ lần cuối
#         else:
#             score['city'] = -0.5

#         # Tìm và xóa lần xuất hiện cuối cùng của key[1] (huyện)
#         district_pos = input.rfind(keys[1])  
#         if district_pos != -1:  # Nếu key[1] có trong input
#             score['district'] = 1  # Cộng 1 điểm cho district
#             input = input[:district_pos] + input[district_pos + len(keys[1]):]+ " "  # Cắt bỏ key[1] chỉ lần cuối
#         else:
#             score['district'] = -0.3

#         # Tìm và xóa lần xuất hiện cuối cùng của key[2] (phường)
#         ward_pos = input.rfind(keys[2]) 
#         if ward_pos != -1:  # Nếu key[2] có trong input
#             score['ward'] = 1  # Cộng 1 điểm cho ward
#             input = input[:ward_pos] + input[ward_pos + len(keys[2]):] + " "  # Cắt bỏ key[2] chỉ lần cuối
#         else:
#             score['ward'] = -0.1
        
#     return score



# def extract_address(user_input, result): 

#     user_input_tmp = remove_accents(user_input)

#     if result['city_score'] == 1 and result['district_score'] != 1 and result['ward_score'] != 1:
#         """Cắt phần địa chỉ trước chuỗi ngăn cách từ user_input_tmp."""
#         for delimiter in delimiters_city:
#             # Tạo biểu thức regex để tìm phần địa chỉ trước delimiter
#             pattern = rf"(.*?)\s*{re.escape(delimiter)}"
#             match = re.search(pattern, user_input_tmp)

#             if match:
#                 # Lấy vị trí của delimiter
#                 delimiter_start = match.end(1)  
#                 # Cắt trên user_input và trả về kết quả
#                 return user_input[:delimiter_start].strip().rstrip(",")

#         # Nếu không tìm thấy trong delimiters_city, kiểm tra với city
#         pattern = rf"(.*?)\s*{re.escape(nomalize_vn(result['city']))}"
#         match = re.search(pattern, user_input_tmp, re.IGNORECASE)  
#         if match:
#             # Lấy vị trí của city
#             city_start = match.end(1)  

#             # Cắt trên user_input và trả về kết quả
#             return user_input[:city_start].strip().rstrip(",")
          
#     #########################################################
    
#     if result['district_score'] == 1 and result['city_score'] == 1 and result['ward_score'] != 1:
#         """Cắt phần địa chỉ trước chuỗi ngăn cách từ user_input."""
#         for delimiter in delimiters_district:
#             # Tạo biểu thức regex để tìm phần địa chỉ trước delimiter
#             pattern = rf"(.*?)\s*{re.escape(delimiter)}"
#             match = re.search(pattern, user_input_tmp)

#             if match:
#                 # Lấy vị trí của delimiter
#                 delimiter_start = match.end(1)  
#                 # Cắt trên user_input và trả về kết quả
#                 return user_input[:delimiter_start].strip().rstrip(",")

#         # Kiểm tra chuỗi P+số hoặc p+số đầu tiên
#         pattern_p = r'(?i)(.*?)(?=\s*Q[0-9]|\sq[0-9])' 
#         match_p = re.search(pattern_p, user_input_tmp)
        

#         if match:
#             # Lấy vị trí của delimiter
#             delimiter_start = match.end(1)  
#             # Cắt trên user_input và trả về kết quả
#             return user_input[:delimiter_start].strip().rstrip(",")

#         pattern = rf"(.*?)\s*{re.escape(nomalize_vn(result['district']))}"
#         match = re.search(pattern, user_input_tmp, re.IGNORECASE)  
#         if match:
#             # Lấy vị trí của delimiter
#             delimiter_start = match.end(1)  
#             # Cắt trên user_input và trả về kết quả
#             return user_input[:delimiter_start].strip().rstrip(",")
        
#     #########################################################   
    
#     if result['ward_score'] == 1 and result['city_score'] == 1 and result['district_score'] == 1:
#         """Cắt phần địa chỉ trước chuỗi ngăn cách từ user_input."""
#         for delimiter in delimiters_ward:
#             # Tạo biểu thức regex để tìm phần địa chỉ trước delimiter
#             pattern = rf"(.*?)\s*{re.escape(delimiter)}"
#             match = re.search(pattern, user_input_tmp)

#             if match:
#                 # Lấy vị trí của delimiter
#                 delimiter_start = match.end(1)
#                 # Cắt trên user_input và trả về kết quả
#                 return user_input[:delimiter_start].strip().rstrip(",")

#         # Kiểm tra chuỗi P+số hoặc p+số đầu tiên
#         pattern_p = r'(?i)(.*?)(?=\s*P[0-9]|\sp[0-9])' 
#         match_p = re.search(pattern_p, user_input_tmp)

#         if match_p:
#             # Lấy vị trí của delimiter
#             delimiter_start = match_p.end(1)  
#             # Cắt trên user_input và trả về kết quả
#             return user_input[:delimiter_start].strip().rstrip(",")

#         pattern = rf"(.*?)\s*{re.escape(nomalize_vn(result['ward']))}"
#         match = re.search(pattern, user_input_tmp, re.IGNORECASE)  
#         if match:
#             # Lấy vị trí của delimiter
#             delimiter_start = match.end(1)  
#             # Cắt trên user_input và trả về kết quả
#             return user_input[:delimiter_start].strip().rstrip(",")
          
#     #######################################################
#     return user_input


    
# def find_best_matches(formatted_input, data, user_input):
#     """Tìm kiếm các địa chỉ tốt nhất dựa trên input của người dùng."""
#     results = []

#     for entry in data:
#         score = calculate_score(formatted_input, entry['keys'])
#         total_score = sum(score.values())  

#         if total_score > 0:
#             results.append({
#                 'city': entry['city'],
#                 'city_id': entry['city_id'],
#                 'district': entry['district'],
#                 'district_id': entry['district_id'],
#                 'ward': entry['ward'],
#                 'ward_id': entry['ward_id'],
#                 'score': total_score,
#                 'ward_score': score['ward'],
#                 'district_score': score['district'],
#                 'city_score': score['city']
#             })

#     # Sắp xếp kết quả theo điểm tổng
#     results.sort(key=lambda x: x['score'], reverse=True)
#     results_tmp = results[:5]
    
#     # Lọc qua top 5 results_tmp, cắt user_input lấy vị trí cụ thể là phần phía trước ward
#     for result in results_tmp:
#             result['address'] = extract_address(user_input, result)

#     return results_tmp

# def find_best(formatted_input, data, user_input):
#     """Tìm kiếm địa chỉ tốt nhất dựa trên input của người dùng."""
#     best_match = None
#     highest_score = float('-inf')  # Khởi tạo điểm cao nhất với giá trị âm vô cực

#     for entry in data:
#         score = calculate_score(formatted_input, entry['keys'])
#         total_score = sum(score.values())

#         if total_score > highest_score:  # Chỉ lưu lại nếu điểm cao hơn
#             highest_score = total_score
#             best_match = {
#                 'city': entry['city'],
#                 'city_id': entry['city_id'],
#                 'district': entry['district'],
#                 'district_id': entry['district_id'],
#                 'ward': entry['ward'],
#                 'ward_id': entry['ward_id'],
#                 'score': total_score,
#                 'ward_score': score['ward'],
#                 'district_score': score['district'],
#                 'city_score': score['city']
#             }

#     if best_match: 
#             best_match['address'] = extract_address(user_input, best_match)

#     return best_match