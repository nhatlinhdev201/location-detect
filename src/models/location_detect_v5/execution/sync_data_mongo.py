import pandas as pd
from src.models.location_detect_v5.execution.format_data_utils import nomalize_vn, format_zero

def remove_whitespace(input_string):
    return input_string.replace(" ", "")

#Lấy lại chỉ số Quận 
def extract_district_number_or_name(ward_name):
    # Tách tên Quận và loại bỏ "Quận"
    number_or_name = ward_name.replace("Quận", "").strip()
    # Trả về chuỗi số hoặc tên Quận
    return str(int(number_or_name)) if number_or_name.isdigit() else number_or_name

#Lấy lại chỉ số phường 
def extract_ward_number_or_name(ward_name):
    ward_name = remove_whitespace(ward_name)
    # Tách tên phường và loại bỏ "Phường"
    number_or_name = ward_name.replace("Phường", "").strip()
    # Trả về chuỗi số nếu là số, ngược lại trả về tên phường
    return str(int(number_or_name)) if number_or_name.isdigit() else number_or_name


def process_api_data(data_list):

    # Kiểm tra kiểu dữ liệu của data_list
    if not isinstance(data_list, list):
        raise ValueError("data_list phải là một danh sách")
    
    data_list = [
    {
        "city_id": addr.city_id,
        "city_name": addr.city_name,
        "district_id": addr.district_id,
        "district_name": addr.district_name,
        "ward_id": addr.ward_id,
        "ward_name": addr.ward_name,
    }
    for addr in data_list
]

    if not all(isinstance(item, dict) for item in data_list):
        raise ValueError("Mỗi phần tử trong data_list phải là một từ điển")

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data_list)

    required_columns = ['city_name', 'city_id', 'district_name', 'district_id', 'ward_name', 'ward_id']
    
    for column in required_columns:
        if column not in df.columns:
            df[column] = None  

    # Lọc các cột cần thiết
    df_filtered = df[required_columns].copy()

    # Xóa bản sao và tạo bản sao mới
    df_unique = df_filtered.drop_duplicates().copy() 

    # Đồng bộ hóa định dạng dữ liệu
    df_unique['district_name'] = df_unique['district_name'].apply(
        lambda x: f"Quận {int(x)}" if str(x).isdigit() else f"Quận {int(x.strip())}" if x.strip().isdigit() else x.strip()
    )
    df_unique['ward_name'] = df_unique['ward_name'].apply(
        lambda x: f"Phường {int(x)}" if str(x).isdigit() else f"Phường {int(x.strip())}" if x.strip().isdigit() else x.strip()
    )

    # Tạo cột keys
    df_unique['district_nomal'] = df_unique['district_name'].apply(extract_district_number_or_name)
    df_unique['ward_nomal'] = df_unique['ward_name'].apply(extract_ward_number_or_name)
    df_unique['city_nomal'] = df_unique['city_name'].apply(lambda x: nomalize_vn(x))

    df_unique['keys'] = df_unique.apply(lambda row: [row['city_nomal'].replace(" ", ""),row['district_nomal'].replace(" ", ""),row['ward_nomal'].replace(" ", "")], axis=1)

    # Chuyển đổi thành định dạng json
    json_data = df_unique[['city_name', 'district_name', 'ward_name', 'district_id', 'ward_id', 'city_id','keys', 'city_nomal', 'district_nomal', 'ward_nomal']].to_dict(orient='records')

    return json_data


def process_api_data_location(data_list):

    # Kiểm tra kiểu dữ liệu của data_list
    if not isinstance(data_list, list):
        raise ValueError("data_list phải là một danh sách")
    
    data_list = [
    {
        "id": addr.id,
        "name": addr.name,
        "code_local": addr.code_local,
        "type": addr.type,
        "parent_id": addr.parent_id,
    }
    for addr in data_list
]

    if not all(isinstance(item, dict) for item in data_list):
        raise ValueError("Mỗi phần tử trong data_list phải là một từ điển")

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data_list)

    required_columns = ['id', 'name', 'code_local', 'type', 'parent_id']
    
    for column in required_columns:
        if column not in df.columns:
            df[column] = None  

    # Lọc các cột cần thiết
    df_filtered = df[required_columns].copy()

    # Xóa bản sao và tạo bản sao mới
    df_unique = df_filtered.drop_duplicates().copy() 

    # Chuyển đổi thành định dạng json
    json_data = df_unique[['id', 'name', 'code_local', 'type', 'parent_id']].to_dict(orient='records')

    return json_data



def serialize_document(doc):
    doc_copy = doc.copy() 
    doc_copy.pop('_id', None) 
    return doc_copy