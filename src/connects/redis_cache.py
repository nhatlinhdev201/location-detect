import aioredis
import os
from dotenv import load_dotenv

load_dotenv()

# Lấy thông tin cấu hình từ môi trường (env)
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_password = os.getenv('REDIS_PASSWORD', '')

# Kết nối tới Redis
redis_cl = aioredis.from_url(
    f"redis://{redis_host}:{redis_port}",
    password=redis_password,  # Thêm mật khẩu vào kết nối Redis
    encoding="utf-8", 
    decode_responses=True
)

