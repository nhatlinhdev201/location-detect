# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URI = os.getenv('MONGO_URI')
# DATABASE_NAME = os.getenv('DATABASE_NAME')

# class MongoDB:
#     def __init__(self, uri: str, db_name: str):
#         self.client = AsyncIOMotorClient(uri)
#         self.db = self.client[db_name]

#     async def get_collection(self, collection_name: str):
#         return self.db[collection_name]

# mongo_db = MongoDB(MONGO_URI, DATABASE_NAME)