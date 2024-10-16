import pandas as pd
import json
from src.utils.format_data_utils import format_address, nomalize_vn

# Đọc dữ liệu Excel
file_path = 'data.xlsx'  # Đảm bảo đường dẫn đúng đến file Excel
df = pd.read_excel(file_path)

# Đổi tên cột
columns = {
    'RecipientAddress': 'address',
    'CityRecipientCode': 'city',
    'CityRecipientId': 'city_id',
    'District': 'district',
    'DistrictID_To': 'district_id',
    'Wards': 'ward',
    'WardId': 'ward_id'
}
df.rename(columns=columns, inplace=True)

# Format đồng bộ dữ liệu
df['district'] = df['district'].apply(lambda x: f"Quận {x}" if isinstance(x, (int, float)) else x)
df['ward'] = df['ward'].apply(lambda x: f"Phường {x}" if isinstance(x, (int, float)) else x )
df['city'] = df['city'].apply(lambda x: x)

df['address'] = df['address'].apply(lambda x: format_address(x))

# Tạo cột keys dạng mảng kết hợp từ các cột city, district, ward
df['district_nomal'] = df['district'].apply(lambda x: nomalize_vn(x))
df['ward_nomal'] = df['ward'].apply(lambda x: nomalize_vn(x))
df['city_nomal'] = df['city'].apply(lambda x: nomalize_vn(x))

df['keys'] = df.apply(lambda row: [row['city_nomal'], row['district_nomal'], row['ward_nomal']], axis=1)

# Xuất dữ liệu
columns_out = ['city', 'city_id', 'district', 'district_id', 'ward', 'ward_id', 'keys']
data = df[columns_out]
data_list = data.to_dict(orient='records')

output_file = 'DataLocation.json'  # Đảm bảo xuất ra đúng vị trí
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(data_list, json_file, ensure_ascii=False, indent=4)   

print('Done!')
