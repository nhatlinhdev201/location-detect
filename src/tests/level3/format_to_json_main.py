import pandas as pd 
import json
import os
from format_data_utils import nomalize_vn, format_zero

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(current_dir, '../../data/data2.xlsx')
out_file_path = os.path.join(current_dir, '../../data/json_data_location.json')

# Đọc file xlsx
df = pd.read_excel(input_file_path)

# Đổi tên cột
df = df.rename(columns={
    'City_name': 'city',
    'City_id': 'city_id',
    'District_name': 'district',
    'District_id': 'district_id',
    'Ward_name': 'ward',
    'Ward_id': 'ward_id'
})
# Chọn các cột cần thiết và tạo bản sao
columns_to_export = ['city', 'city_id', 'district', 'district_id', 'ward', 'ward_id']  
df_filtered = df[columns_to_export].copy()  

# Xóa bản sao và tạo bản sao mới
df_unique = df_filtered.drop_duplicates().copy() 

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
json_data = df_unique[['city', 'district', 'ward', 'district_id', 'ward_id', 'city_id', 'keys']].to_dict(orient='records')


# write to file
json_ouput = json.dumps(json_data, ensure_ascii=False, indent=4)
with open(out_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(json_ouput)

print('Done!')