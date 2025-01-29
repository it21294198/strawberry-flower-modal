import logging

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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



# postgresql connection manager
class PostgresManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def connect(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.session_factory = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        print("Connected to Postgres")

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            print("Closed Postgres connection")

    def get_session(self) -> AsyncSession:
        return self.session_factory()



# connection creator for both at once
class DatabaseManager:
    def __init__(self):
        self.mongo_manager = MongoDBManager()
        self.pg_manager = PostgresManager()


    async def connect_all(self, mongo_uri: str, mongo_db_name: str, pg_url: str):
        try:
            await self.mongo_manager.connect(mongo_uri, mongo_db_name)
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            return  # prevent proceeding if MongoDB fails

        try:
            await self.pg_manager.connect(pg_url)
        except Exception as e:
            logging.error(f"Failed to connect to Postgres: {e}")
            # await self.mongo_manager.close()  # rollback MongoDB connection


    async def close_all(self):
        await self.mongo_manager.close()
        await self.pg_manager.close()


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

        # check Postgres
        try:
            if self.pg_manager.engine:
                async with self.pg_manager.get_session() as session:
                    await session.execute("SELECT 1")  # simple query to test connection
                    health_status["postgres"] = "healthy"
            else:
                health_status["postgres"] = "not connected"
        except Exception as e:
            health_status["postgres"] = f"unhealthy: {str(e)}"

        return health_status
