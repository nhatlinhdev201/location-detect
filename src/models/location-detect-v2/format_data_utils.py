# import re
# import unicodedata

# replacements = [
#     {"key": " p.", "value": " phuong "},
#     {"key": " p ", "value": " phuong "},
#     {"key": " h ", "value": " "},
#     {"key": " h.", "value": " "},
#     {"key": " q ", "value": " quan "},
#     {"key": " q.", "value": " quan "},
#     {"key": " tx ", "value": " "},
#     {"key": " tx.", "value": " "},
#     {"key": " tp ", "value": " "},
#     {"key": " tp.", "value": " "},
#     {"key": " hcm", "value": " ho chi minh "},
#     {"key": " tphcm", "value": " ho chi minh "},
# ]

# def format_zero(text):
#     # Sử dụng regex để thay thế "Phường 0X" thành "Phường X"
#     return re.sub(r'(phuong) 0([1-9])', r'\1 \2', text)

# def format_number(text):
#     # Thay thế "phường 0X" thành "phường X" (X là số từ 1 đến 9)
#     text = re.sub(r'(phuong) 0([1-9])', r'\1 \2', text)

#     # Thay thế "quận 0X" thành "quận X" (X là số từ 1 đến 9)
#     text = re.sub(r'(quan) 0([1-9])', r'\1 \2', text)

#     # # Thay thế "P0X" hoặc "PX" thành "phường X" (X là số từ 1 đến 9)
#     # text = re.sub(r'P0?([1-9])', r'phuong \1', text)

#     # # Thay thế "Q0X" hoặc "QX" thành "quận X" (X là số từ 1 đến 9)
#     # text = re.sub(r'Q0?([1-9])', r'quan \1', text)

#     # Thay thế "p0X" hoặc "pX" thành "phường X" (X là số từ 1 đến 9)
#     text = re.sub(r'p0?([1-9])', r'phuong \1', text)

#     # Thay thế "q0X" hoặc "qX" thành "quận X" (X là số từ 1 đến 9)
#     text = re.sub(r'q0?([1-9])', r'quan \1', text)

#     # Thay thế "P+số" (số từ 1 đến 9) thành "phường + số" (tránh thay thế P0)
#     # text = re.sub(r'P([1-9])', r'phuong \1', text)   # Xử lý với P1 - P9

#     # # Thay thế "Q+số" (số từ 1 đến 9) thành "quận + số" (tránh thay thế Q0)
#     # text = re.sub(r'Q([1-9])', r'quan \1', text)     # Xử lý với Q1 - Q9

#      # Thay thế "P+số" (số từ 1 đến 9) thành "phường + số" (tránh thay thế P0)
#     text = re.sub(r'p([1-9])', r'phuong \1', text)   # Xử lý với P1 - P9

#     # Thay thế "Q+số" (số từ 1 đến 9) thành "quận + số" (tránh thay thế Q0)
#     text = re.sub(r'q([1-9])', r'quan \1', text)     # Xử lý với Q1 - Q9

#     return text

# def remove_accents(text):
#     text = text.lower()

#     """Loại bỏ dấu tiếng Việt và chuyển đổi ký tự có dấu thành ký tự không dấu."""
#     # Chuyển đổi thành dạng NFKD để tách các dấu
#     nfkd_form = unicodedata.normalize('NFKD', text)
    
#     # Loại bỏ các dấu
#     text_without_accents = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
#     # Thay thế các ký tự cụ thể
#     text_without_accents = text_without_accents.replace('đ', 'd').replace('Đ', 'D')
    
#     return text_without_accents

# def format_address(address):
#     # Bước 1: Chuyển chuỗi về dạng chữ thường và không dấu
#     address = remove_accents(address)
#     address = address.replace(",", " ")


#      # Bước 3: Thay thế các từ khóa
#     for replacement in replacements:
#         key = replacement['key']
#         value = replacement['value']
#         address = address.replace(key, value)

#     # Bước 2: Thay thế các ký tự đặc biệt cụ thể bằng khoảng trắng
#     special_chars = ['#', '!', '.', '-']
#     for char in special_chars:
#         address = address.replace(char, ' ')
    
#     # Bước 4: Xử lý "Phường 0X"
#     address = format_number(address)
    
#     # Bước 5: Bỏ đi các khoảng trắng thừa
#     address = re.sub(r'\s+', ' ', address).strip()
    
#     return " "+address+" "

# # chuyen ve dong bo tieng viet khong dau
# def nomalize_vn(text):
#     text = text.lower()
#     text = remove_accents(text)
#     return text

# def check_phone_number(input_string: str) -> bool:
#     vietnam_phone_pattern = r'(?<!\d)(0[1-9]{1}[0-9]{8}|(?:\+84|84)[1-9]{1}[0-9]{8})(?!\d)'
#     international_phone_pattern = r'(?<!\d)(\+?\d{1,3}[- ]?)?\d{10}(?!\d)'

#     combined_pattern = f'({vietnam_phone_pattern})|({international_phone_pattern})'

#     if re.search(combined_pattern, input_string):
#         return False
#     return True 