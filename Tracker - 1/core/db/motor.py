import logging

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from core.config.settings import get_settings

# Module-level logger instance
logger = logging.getLogger(__name__)

# Load application settings
settings = get_settings()


class Database:
    """
    MongoDB database connection manager.

    Handles:
    - connection initialization
    - connectivity validation
    - graceful shutdown
    - database instance access
    """

    def __init__(self) -> None:
        """
        Initialize database connection state.
        """

        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """
        Initialize MongoDB connection and validate connectivity.

        The ping command forces MongoDB server selection
        during application startup, helping fail fast if
        the database is unavailable.
        """

        self.client = AsyncIOMotorClient(
            settings.mongo_uri,

            # Maximum simultaneous connections
            maxPoolSize=50,

            # Minimum idle connections maintained
            minPoolSize=5,

            # Timeout for server selection
            serverSelectionTimeoutMS=5000,
        )

        # Validate MongoDB connectivity
        await self.client.admin.command("ping")

        # Select application database
        self.db = self.client[settings.mongo_db]

        # Create indexes during startup if needed
        # await self._create_indexes()

        logger.info("MongoDB connected successfully")

    async def disconnect(self) -> None:
        """
        Gracefully close MongoDB connection.

        Clears internal references after shutdown.
        """

        if self.client is not None:
            self.client.close()

        self.client = None
        self.db = None

        logger.info("MongoDB connection closed")

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Return active MongoDB database instance.

        Raises:
            RuntimeError:
                If the database connection has not
                been initialized yet.

        Returns:
            Active MongoDB database object.
        """

        if self.db is None:
            raise RuntimeError(
                "Database not connected. "
                "Ensure application startup completed."
            )

        return self.db


# Shared database manager instance
database = Database()