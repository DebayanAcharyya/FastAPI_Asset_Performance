from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import dotenv_values

config = dotenv_values(".env")
uri = config["MONGO_URI"]
database = config["DB_NAME"]

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = AsyncIOMotorClient(uri)
            cls._instance.db = cls._instance.client[database]
        return cls._instance
    
# Function to close the MongoDB connection
async def close_database_client():
    Database().client.close()
    

