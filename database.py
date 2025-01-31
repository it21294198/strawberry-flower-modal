import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict

# MongoDB connection manager
class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self, uri: str, database_name: str):
        """
        Connects to MongoDB using the provided URI and database name.
        """
        try:
            self.client = AsyncIOMotorClient(uri)
            self.db = self.client[database_name]
            logging.info("Connected to MongoDB")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        """
        Closes the MongoDB connection if it exists.
        """
        if self.client:
            self.client.close()
            logging.info("Closed MongoDB connection")


# Database connection manager
class DatabaseManager:
    def __init__(self):
        self.mongo_manager = MongoDBManager()

    async def connect_all(self, mongo_uri: str, mongo_db_name: str):
        """
        Connects to all necessary databases (currently only MongoDB).
        """
        try:
            await self.mongo_manager.connect(mongo_uri, mongo_db_name)
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close_all(self):
        """
        Closes all database connections.
        """
        await self.mongo_manager.close()

    async def add_to_mongo(self, data: Dict, collection_name: str = "operations"):
        """
        Adds a document to the specified MongoDB collection.

        Args:
            data (Dict): The data to insert into the MongoDB collection.
            collection_name (str): The name of the MongoDB collection (default: "operations").
        """
        try:
            collection = self.mongo_manager.db[collection_name]  # Access the MongoDB collection
            result = await collection.insert_one(data)  # Insert the document
            logging.info(f"Document added to MongoDB with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logging.error(f"Failed to add data to MongoDB: {e}")
            raise

    async def check_health(self):
        """
        Checks the health of all database connections.

        Returns:
            dict: A dictionary containing the health status of each database.
        """
        health_status = {"mongo": "unknown"}

        # Check MongoDB health
        try:
            if self.mongo_manager.db is not None:
                await self.mongo_manager.db.command("ping")  # MongoDB ping command
                health_status["mongo"] = "healthy"
            else:
                health_status["mongo"] = "not connected"
        except Exception as e:
            logging.error(f"MongoDB health check failed: {e}")
            health_status["mongo"] = f"unhealthy: {str(e)}"

        return health_status


