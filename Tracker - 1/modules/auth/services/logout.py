from datetime import datetime, timezone

from modules.auth.protocols import BlacklistedTokenWrite, BlacklistedTokenRead
from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel
from modules.auth.exceptions import InvalidTokenError

from core.security.jwt import verify_access_token
from core.events.event_bus import EventBus


class LogoutService:
    def __init__(
        self,
        blacklisted_token_write: BlacklistedTokenWrite,
        blacklisted_token_read: BlacklistedTokenRead,
        event_bus: EventBus,  # FIX #11: injected event bus
    ) -> None:
        self.blacklisted_token_write = blacklisted_token_write
        self.blacklisted_token_read = blacklisted_token_read
        self.event_bus = event_bus

    async def execute(self, token: str) -> None:

        payload = verify_access_token(token)

        if not payload:
            raise InvalidTokenError()

        jti = payload["jti"]

        # Already blacklisted — silently succeed
        if await self.blacklisted_token_read.is_token_blacklisted(jti):
            return

        blacklisted_token = BlacklistedTokenModel(
            jti=jti,
            user_id=payload["sub"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )

        await self.blacklisted_token_write.create_blacklisted_token(blacklisted_token)

        # FIX #11: publish event — no-op today, real broker tomorrow
        await self.event_bus.publish(
            "user.logged_out",
            {"user_id": payload["sub"], "jti": jti},
        )