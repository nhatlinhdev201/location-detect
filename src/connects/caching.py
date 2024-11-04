from cachetools import TTLCache
import os
from dotenv import load_dotenv

load_dotenv()

# Lấy cấu hình từ biến môi trường hoặc gán giá trị mặc định
CACHE_TIME = int(os.getenv('CACHE_TIME', 3600))  # Thời gian sống của cache (giây)
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 100))  # Kích thước tối đa của cache

# Khởi tạo cache với TTL
lru_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TIME)
