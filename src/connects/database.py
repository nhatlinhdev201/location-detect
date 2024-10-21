from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pymongo.errors import PyMongoError  # Vẫn giữ import này

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

client = AsyncIOMotorClient(MONGO_URI)
db = client["your_database_name"] 

async def get_database():
    try:
        await client.admin.command('ping') 
        print("Kết nối tới MongoDB đã được thiết lập thành công.")
        return db  
    except PyMongoError:
        print("Không thể kết nối tới MongoDB.")
        return None
