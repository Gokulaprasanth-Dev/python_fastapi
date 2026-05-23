import logging

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Database:
    """
    MongoDB database connection manager.

    Handles:
    - connection initialization
    - connectivity validation
    - graceful shutdown
    - database and client instance access
    """

    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        self.client = AsyncIOMotorClient(
            settings.mongo_uri,
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,
        )

        await self.client.admin.command("ping")
        self.db = self.client[settings.mongo_db]

        logger.info("MongoDB connected successfully")

    async def disconnect(self) -> None:
        if self.client is not None:
            self.client.close()

        self.client = None
        self.db = None

        logger.info("MongoDB connection closed")

    def get_database(self) -> AsyncIOMotorDatabase:
        if self.db is None:
            raise RuntimeError(
                "Database not connected. "
                "Ensure application startup completed."
            )
        return self.db

    def get_client(self) -> AsyncIOMotorClient:
        """
        Return the active Motor client.

        Used by MongoUnitOfWork to start sessions for transactions.

        Raises:
            RuntimeError: If the client has not been initialised yet.
        """
        if self.client is None:
            raise RuntimeError(
                "Database not connected. "
                "Ensure application startup completed."
            )
        return self.client


database = Database() 