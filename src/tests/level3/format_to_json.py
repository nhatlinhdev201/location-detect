import pandas as pd 
import json
import os
from format_data_utils import nomalize_vn, format_zero

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(current_dir, '../../data/data.xlsx')
out_file_path = os.path.join(current_dir, '../../data/json_data_location_level3.json')

# Đọc file xlsx
df = pd.read_excel(input_file_path)

# Đổi tên cột
df = df.rename(columns={
    'CityRecipientCode': 'city',
    'CityRecipientId': 'city_id',
    'District': 'district',
    'DistrictID_To': 'district_id',
    'Wards': 'ward',
    'WardId': 'ward_id'
})

# Chọn các cột cần thiết và tạo bản sao
columns_to_export = ['city', 'city_id', 'district', 'district_id', 'ward', 'ward_id']  
df_filtered = df[columns_to_export].copy()  # Thêm .copy() ở đây

# Xóa bản sao và tạo bản sao mới
df_unique = df_filtered.drop_duplicates().copy()  # Thêm .copy() ở đây

# Đồng bộ hóa định dạng dữ liệu
df_unique.loc[:, 'district'] = df_unique['district'].apply(lambda x: f"Quận {x}" if isinstance(x, (int, float)) else x)
df_unique.loc[:, 'ward'] = df_unique['ward'].apply(lambda x: f"Phường {x}" if isinstance(x, (int, float)) else x)
df_unique.loc[:, 'city'] = df_unique['city'].apply(lambda x: x)

# Tạo cột keys
df_unique.loc[:, 'district_nomal'] = df_unique['district'].apply(lambda x: nomalize_vn(x))
df_unique.loc[:, 'ward_nomal'] = df_unique['ward'].apply(lambda x: format_zero(nomalize_vn(x)))
df_unique.loc[:, 'city_nomal'] = df_unique['city'].apply(lambda x: nomalize_vn(x))

df_unique.loc[:, 'keys'] = df_unique.apply(lambda row: [row['ward_nomal'], row['district_nomal'], row['city_nomal']], axis=1)

# Chuyển đổi thành định dạng json
# Chọn cột xuất ra (có thể chọn những cột bạn muốn)
json_data = df_unique[['city', 'district', 'ward', 'district_id', 'ward_id', 'city_id', 'keys']].to_dict(orient='records')


# write to file
json_ouput = json.dumps(json_data, ensure_ascii=False, indent=4)
with open(out_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(json_ouput)

print('Done!')