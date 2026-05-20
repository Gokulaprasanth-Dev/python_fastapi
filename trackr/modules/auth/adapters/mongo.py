"""
MongoTokenBlacklistAdapter — persists revoked JTIs in the `token_blacklist` collection.

The collection has a TTL index on `expires_at` (created in core/db/motor.py
during init_db). MongoDB automatically removes documents once expires_at
passes, so the blacklist never grows unboundedly.

No Depends(), no FastAPI, no HTTP concepts here.
"""

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoTokenBlacklistAdapter:
    COLLECTION = "token_blacklist"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]

    async def add(self, jti: str, expires_at: datetime) -> None:
        """Record a revoked JTI. Duplicate inserts are silently ignored."""
        await self._col.update_one(
            {"_id": jti},
            {"$setOnInsert": {"_id": jti, "expires_at": expires_at}},
            upsert=True,
        )

    async def is_revoked(self, jti: str) -> bool:
        doc = await self._col.find_one({"_id": jti}, {"_id": 1})
        return doc is not None
