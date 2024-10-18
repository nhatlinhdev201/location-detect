import re
import unicodedata

replacements = [
    {"key": " p ", "value": " phuong "},
    {"key": " h ", "value": " "},
    {"key": " tx ", "value": " "},
    {"key": " tp ", "value": " "},
    {"key": " hcm", "value": " ho chi minh"},
    {"key": " 0", "value": " "},
]

def format_phuong(text):
    # Sử dụng regex để thay thế "Phường 0X" thành "Phường X"
    return re.sub(r'(Phường) 0([1-9])', r'\1 \2', text)

def remove_accents(text):
    """Loại bỏ dấu tiếng Việt."""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def format_address(address):
    # buoc 1 : chuyen het ve khong dau viet thuong
    address = address.lower()
    address = remove_accents(address)

    # buoc 2 : thay the các kieu ky tu dac biet
    special_chars = ['#', '!', ',', '.', '-']
    for char in special_chars:
        address = address.replace(char, ' ')

     # buoc 3 : thay the tung kieu ky tu
    for replacement in replacements:
        key = replacement['key']
        value = replacement['value']
        address = address.replace(key, value)
    
    # buoc 4 : bo cac khoang trang thua
    address = re.sub(r'\s+', ' ', address).strip()
    
    return address

# chuyen ve dong bo tieng viet khong dau
def nomalize_vn(text):
    text = text.lower()
    text = remove_accents(text)
    return text