from cachetools import LRUCache
from datetime import datetime, timedelta, timezone  # Thêm timezone vào import
from dotenv import load_dotenv
import os

load_dotenv()

CACHE_TIME = int(os.getenv('CACHE_TIME', 3600))  
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 100)) 

class TTLCache(LRUCache):
    def __init__(self, maxsize=3000, ttl=3600):
        super().__init__(maxsize)
        self.ttl = ttl
        self.expiry = {}

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        # Sử dụng timezone.utc để lấy thời gian UTC
        self.expiry[key] = datetime.now(timezone.utc) + timedelta(seconds=self.ttl)

    def __getitem__(self, key):
        if key in self.expiry and datetime.now(timezone.utc) > self.expiry[key]:
            del self[key] 
            raise KeyError(f"{key} has expired")
        return super().__getitem__(key)

# Khởi tạo cache với TTL
lru_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TIME)
