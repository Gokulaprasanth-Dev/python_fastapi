# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
# from pymongo import ASCENDING

# from core.config.settings import get_settings

# _client: AsyncIOMotorClient | None = None  # type: ignore[type-arg]


# async def init_db(uri: str, db_name: str) -> None:
#     global _client
#     _client = AsyncIOMotorClient(uri)
#     # Ping to catch bad URIs early
#     await _client.admin.command("ping")
#     await _create_indexes(_client[db_name])


# async def _create_indexes(db: AsyncIOMotorDatabase) -> None:  # type: ignore[type-arg]
#     """
#     Idempotent index creation — safe to call on every startup.

#     token_blacklist.expires_at TTL index:
#       MongoDB removes documents automatically once expires_at is in the past.
#       expireAfterSeconds=0 means "delete as soon as the field datetime passes".
#     """
#     await db["users"].create_index("email", unique=True, background=True)
#     await db["users"].create_index("company_id", background=True)
#     await db["companies"].create_index("name", background=True)
#     await db["token_blacklist"].create_index(
#         [("expires_at", ASCENDING)],
#         expireAfterSeconds=0,
#         background=True,
#         name="ttl_expires_at",
#     )


# async def shutdown_db() -> None:
#     global _client
#     if _client is not None:
#         _client.close()
#         _client = None


# def get_db() -> AsyncIOMotorDatabase:  # type: ignore[type-arg]
#     if _client is None:
#         raise RuntimeError("DB not initialised -- call init_db() first")
#     return _client[get_settings().mongo_db]


import logging

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)
from pymongo import ASCENDING

from core.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class Database:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """
        Initialize MongoDB connection and validate connectivity.
        """

        self.client = AsyncIOMotorClient(
            settings.mongo_uri,
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,
        )

        # Force connection validation during startup
        await self.client.admin.command("ping")

        self.db = self.client[settings.mongo_db]

        # await self._create_indexes()

        logger.info("MongoDB connected successfully")

    async def disconnect(self) -> None:
        """
        Gracefully close MongoDB connection.
        """
  
        if self.client is not None:
            self.client.close()

        self.client = None
        self.db = None

        logger.info("MongoDB connection closed")

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Return active database instance.
        """

        if self.db is None:
            raise RuntimeError(
                "Database not connected. Ensure application startup completed."
            )

        return self.db

    async def _create_indexes(self) -> None:
        """
        Create indexes safely during startup.
        """

        db = self.get_database()

        await db["users"].create_index(
            "email",
            unique=True,
            name="idx_users_email_unique",
        )

        await db["users"].create_index(
            "company_id",
            name="idx_users_company_id",
        )

        await db["companies"].create_index(
            "name",
            name="idx_companies_name",
        )

        await db["token_blacklist"].create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="idx_token_blacklist_ttl",
        )

        logger.info("MongoDB indexes ensured")


database = Database()

def get_db() -> AsyncIOMotorDatabase:
    return database.get_database()