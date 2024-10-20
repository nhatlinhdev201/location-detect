import re
import unicodedata

replacements = [
    {"key": " p. ", "value": " phuong "},
    {"key": " p ", "value": " phuong "},
    {"key": " h ", "value": " "},
    {"key": " q ", "value": " quan "},
    {"key": " q. ", "value": " quan "},
    {"key": " tx ", "value": " "},
    {"key": " tp ", "value": " "},
    {"key": " hcm", "value": " ho chi minh"},
]

def format_zero(text):
    # Sử dụng regex để thay thế "Phường 0X" thành "Phường X"
    return re.sub(r'(phuong) 0([1-9])', r'\1 \2', text)

def remove_accents(text):
    """Loại bỏ dấu tiếng Việt và chuyển đổi ký tự có dấu thành ký tự không dấu."""
    # Chuyển đổi thành dạng NFKD để tách các dấu
    nfkd_form = unicodedata.normalize('NFKD', text)
    
    # Loại bỏ các dấu
    text_without_accents = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Thay thế các ký tự cụ thể
    text_without_accents = text_without_accents.replace('đ', 'd').replace('Đ', 'D')
    
    return text_without_accents

def format_address(address):
    # Bước 1: Chuyển chuỗi về dạng chữ thường và không dấu
    address = address.lower()
    address = remove_accents(address)

     # Bước 3: Thay thế các từ khóa
    for replacement in replacements:
        key = replacement['key']
        value = replacement['value']
        address = address.replace(key, value)

    # Bước 2: Thay thế các ký tự đặc biệt cụ thể bằng khoảng trắng
    special_chars = ['#', '!', ',', '.', '-']
    for char in special_chars:
        address = address.replace(char, ' ')
    
    # Bước 4: Xử lý "Phường 0X"
    address = format_zero(address)
    
    # Bước 5: Bỏ đi các khoảng trắng thừa
    address = re.sub(r'\s+', ' ', address).strip()
    
    return address

# chuyen ve dong bo tieng viet khong dau
def nomalize_vn(text):
    text = text.lower()
    text = remove_accents(text)
    return text