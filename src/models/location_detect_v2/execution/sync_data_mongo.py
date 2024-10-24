import pandas as pd
from src.models.location_detect_v2.execution.format_data_utils import nomalize_vn, format_zero

def add_phuong_prefix(ward_name):
    if isinstance(ward_name, (int, float)):
        return f"Phường {ward_name}"
    elif isinstance(ward_name, str) and ward_name.isdigit():
        return f"Phường {ward_name}"
    return ward_name

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

    # print(data_list)
    # return 'ok'

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
    df_unique['district_name'] = df_unique['district_name'].apply(lambda x: f"Quận {x}" if isinstance(x, (int, float)) else x)
    # df_unique['ward_name'] = df_unique['ward_name'].apply(lambda x: f"Phường {x}" if isinstance(x, (int, float)) else x)
    df_unique['ward_name'] = df_unique['ward_name'].apply(add_phuong_prefix)

    # Tạo cột keys
    df_unique['district_nomal'] = df_unique['district_name'].apply(lambda x: nomalize_vn(x))
    df_unique['ward_nomal'] = df_unique['ward_name'].apply(lambda x: format_zero(nomalize_vn(x)))
    df_unique['city_nomal'] = df_unique['city_name'].apply(lambda x: nomalize_vn(x))

    df_unique['keys'] = df_unique.apply(lambda row: [" " + row['city_nomal'] + " ", " " + row['district_nomal'] + " ", " " + row['ward_nomal'] + " "], axis=1)

    # Chuyển đổi thành định dạng json
    json_data = df_unique[['city_name', 'district_name', 'ward_name', 'district_id', 'ward_id', 'city_id','keys', 'city_nomal', 'district_nomal', 'ward_nomal']].to_dict(orient='records')

    return json_data


