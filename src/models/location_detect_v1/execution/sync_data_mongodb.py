import pandas as pd
from src.models.location_detect_v1.execution.format_data_utils import nomalize_vn, format_zero

def process_api_data(data_list):

    # Kiểm tra kiểu dữ liệu của data_list
    if not isinstance(data_list, list):
        raise ValueError("data_list phải là một danh sách")
    
    data_list = [
    {
        "id": addr.id,
        "address": addr.address,
        "city_id": addr.city_id,
        "city_name": addr.city_name,
        "district_id": addr.district_id,
        "district_name": addr.district_name,
        "ward_id": addr.ward_id,
        "ward_name": addr.ward_name,
        "street_name": addr.street_name,
        "type_address": addr.type_address
    }
    for addr in data_list
]

    # print(data_list)
    # return 'ok'

    if not all(isinstance(item, dict) for item in data_list):
        raise ValueError("Mỗi phần tử trong data_list phải là một từ điển")

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data_list)

    # Đảm bảo có tất cả các trường cần thiết
    required_columns = ['id','city_name', 'city_id', 'district_name', 'district_id', 'ward_name', 'ward_id', 'address', 'street_name', 'type_address']
    
    for column in required_columns:
        if column not in df.columns:
            df[column] = None  

    # Lọc các cột cần thiết
    df_filtered = df[required_columns].copy()

    # Xóa bản sao và tạo bản sao mới
    df_unique = df_filtered.drop_duplicates().copy() 

    # Đồng bộ hóa định dạng dữ liệu
    df_unique['district_name'] = df_unique['district_name'].apply(lambda x: f"Quận {x}" if isinstance(x, (int, float)) else x)
    df_unique['ward_name'] = df_unique['ward_name'].apply(lambda x: f"Phường {x}" if isinstance(x, (int, float)) else x)

    # Tạo cột keys
    df_unique['district_nomal'] = df_unique['district_name'].apply(lambda x: nomalize_vn(x))
    df_unique['ward_nomal'] = df_unique['ward_name'].apply(lambda x: format_zero(nomalize_vn(x)))
    df_unique['city_nomal'] = df_unique['city_name'].apply(lambda x: nomalize_vn(x))

    df_unique['keys'] = df_unique.apply(lambda row: [" " + row['city_nomal'] + " ", " " + row['district_nomal'] + " ", " " + row['ward_nomal'] + " "], axis=1)

    # Chuyển đổi thành định dạng json
    json_data = df_unique[['id', 'city_name', 'district_name', 'ward_name', 'district_id', 'ward_id', 'city_id', 'address', 'street_name', 'type_address', 'keys']].to_dict(orient='records')

    return json_data


