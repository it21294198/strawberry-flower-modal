# db_manager.py
from database import DatabaseManager

# Global db_manager instance
db_manager = DatabaseManager()

# Function to initialize and connect the database manager
async def connect_db(MONGO_URI: str, MONGO_DB_NAME: str):
    await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME)
    if db_manager.mongo_manager is None:
        raise Exception("Failed to connect to MongoDB")
    else:
        print("Connected to MongoDB")

# Dependency function to get the db_manager instance
def get_db_manager():
    return db_manager
