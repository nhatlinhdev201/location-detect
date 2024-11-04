import re
import unicodedata

replacements = [
    {"key": " p.", "value": " phuong "},
    {"key": " p ", "value": " phuong "},
    {"key": " h ", "value": " "},
    {"key": " h.", "value": " "},
    {"key": " q ", "value": " quan "},
    {"key": " q.", "value": " quan "},
    {"key": " tx ", "value": " "},
    {"key": " tx.", "value": " "},
    {"key": " tp ", "value": " "},
    {"key": " tp.", "value": " "},
    {"key": " hcm", "value": " ho chi minh "},
    {"key": " tphcm", "value": " ho chi minh "},
    {"key": " thanh pho ", "value": " "}
]

def format_zero(text):
    return re.sub(r'(phuong) 0([1-9])', r'\1 \2', text)

def format_number(text):
    text = re.sub(r'\b(phuong|p)(?: 0+)?([1-9])\b', r'phuong \2', text)
    text = re.sub(r'\b(quan|q)(?: 0+)?([1-9])\b', r'quan \2', text)
    return text

def remove_accents(text):
    text = text.lower()
    nfkd_form = unicodedata.normalize('NFKD', text)
    text_without_accents = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    return text_without_accents.replace('đ', 'd').replace('Đ', 'D')

def format_address(address):
    address = remove_accents(address).replace(",", " ")
    
    replacement_pattern = '|'.join([re.escape(replacement['key']) for replacement in replacements])
    address = re.sub(replacement_pattern, 
                      lambda m: next((r['value'] for r in replacements if r['key'] == m.group(0)), m.group(0)), 
                      address)

    address = re.sub(r'[\#\!\.\-]', ' ', address)
    address = format_number(address)
    address = re.sub(r'\s+', ' ', address).strip()
    
    return f" {address} "

def nomalize_vn(text):
    return remove_accents(text)

def check_phone_number(input_string: str) -> bool:
    vietnam_phone_pattern = r'(?<!\d)(0[1-9]{1}[0-9]{8}|(?:\+84|84)[1-9]{1}[0-9]{8})(?!\d)'
    international_phone_pattern = r'(?<!\d)(\+?\d{1,3}[- ]?)?\d{10}(?!\d)'
    combined_pattern = f'({vietnam_phone_pattern})|({international_phone_pattern})'
    return not re.search(combined_pattern, input_string)
