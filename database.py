import logging

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# MongoDB connection manager
class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self, uri: str, database_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
        print("Connected to MongoDB")

    async def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

# connection creator for both at once
class DatabaseManager:
    def __init__(self):
        self.mongo_manager = MongoDBManager()

    async def connect_all(self, mongo_uri: str, mongo_db_name: str):
        try:
            await self.mongo_manager.connect(mongo_uri, mongo_db_name)
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            return  # prevent proceeding if MongoDB fails

    async def close_all(self):
        await self.mongo_manager.close()


    async def check_health(self):
        health_status = {"mongo": "unknown", "postgres": "unknown"}

        # check MongoDB
        try:
            if self.mongo_manager.db:
                await self.mongo_manager.db.command("ping")  # MongoDB ping command
                health_status["mongo"] = "healthy"
            else:
                health_status["mongo"] = "not connected"
        except Exception as e:
            health_status["mongo"] = f"unhealthy: {str(e)}"

        return health_status
