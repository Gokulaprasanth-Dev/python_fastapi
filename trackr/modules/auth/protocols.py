from datetime import datetime
from typing import Protocol


class TokenBlacklist(Protocol):
    async def add(self, jti: str, expires_at: datetime) -> None:
        """Insert a revoked token JTI. expires_at drives the TTL index cleanup."""
        ...

    async def is_revoked(self, jti: str) -> bool:
        """Return True if the JTI has been blacklisted."""
        ...
