from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
database_name = os.getenv('DATABASE_NAME')
host = os.getenv('MONGO_HOST')

# Mã hóa tên người dùng và mật khẩu
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Xây dựng MONGO_URI
MONGO_URI = f"mongodb://{encoded_username}:{encoded_password}@localhost:{host}"

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def get_collection(self, collection_name: str):
        return self.db[collection_name]

mongo_db = MongoDB(MONGO_URI, database_name)
