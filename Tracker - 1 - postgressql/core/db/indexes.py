"""
MongoDB index bootstrap.

Called once at application startup. All indexes are created with
create_if_not_exists semantics (Motor silently skips existing indexes
with matching definitions).

Note: the `background` parameter was removed — it was deprecated in
MongoDB 4.2 and index builds are always non-blocking now. Passing it
produces a deprecation warning in the server logs.

Index rationale:
  users.email         — unique; guards against duplicate registration and
                        enables fast login lookups.
  users.id            — unique; used by every profile read/update path.
  companies.id        — unique; used by company lookups after registration.
  token_blacklist.jti — unique; prevents duplicate blacklist entries and
                        enables O(1) token revocation checks.
  token_blacklist.expires_at (TTL=0) — MongoDB auto-deletes documents
                        whose expires_at has passed, keeping the collection
                        from growing without bound.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create all required indexes. Safe to call on every startup."""

    # ── users ──────────────────────────────────────────────────────────────
    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("id", unique=True)

    # ── companies ──────────────────────────────────────────────────────────
    await db["companies"].create_index("id", unique=True)

    # ── token_blacklist ────────────────────────────────────────────────────
    await db["token_blacklist"].create_index("jti", unique=True)
    # TTL index: MongoDB removes expired token documents automatically.
    await db["token_blacklist"].create_index(
        "expires_at",
        expireAfterSeconds=0,
    )

    logger.info("MongoDB indexes verified / created")
