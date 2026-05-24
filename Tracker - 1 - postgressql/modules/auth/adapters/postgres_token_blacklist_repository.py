from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.tables.token_blacklist_table import TokenBlacklistTable
from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel


class PostgresTokenBlacklistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def is_token_blacklisted(self, jti: str) -> bool:
        result = await self.session.execute(
            select(TokenBlacklistTable.id).where(TokenBlacklistTable.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def create_blacklisted_token(self, data: BlacklistedTokenModel) -> str:
        row = TokenBlacklistTable(
            id=data.id,
            jti=data.jti,
            user_id=data.user_id,
            expires_at=data.expires_at,
        )
        self.session.add(row)
        await self.session.flush()
        return str(data.id)

    async def purge_expired(self) -> int:
        """Delete all expired tokens. Called by the background cleanup task."""
        result = await self.session.execute(
            delete(TokenBlacklistTable).where(
                TokenBlacklistTable.expires_at < datetime.now(timezone.utc)
            )
        )
        await self.session.commit()
        return result.rowcount
