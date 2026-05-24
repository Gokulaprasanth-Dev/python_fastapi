from datetime import datetime, timezone

from jose import JWTError

from modules.auth.protocols import BlacklistedTokenWrite, BlacklistedTokenRead
from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel
from modules.auth.exceptions import InvalidTokenError

from core.security.jwt import verify_access_token, get_token_jti, TokenVerifyResult
from core.events.event_bus import EventBus
from core.events.schemas import UserLoggedOutEvent


class LogoutService:
    def __init__(
        self,
        blacklisted_token_write: BlacklistedTokenWrite,
        blacklisted_token_read: BlacklistedTokenRead,
        event_bus: EventBus,
    ) -> None:
        self.blacklisted_token_write = blacklisted_token_write
        self.blacklisted_token_read = blacklisted_token_read
        self.event_bus = event_bus

    async def execute(self, token: str) -> None:
        result, payload = verify_access_token(token)

        # Fix 2: expired tokens have a valid signature — the user should still
        # be able to logout (blacklist the JTI) even if the token is past expiry.
        # Only hard-reject structurally invalid tokens.
        if result is TokenVerifyResult.INVALID:
            raise InvalidTokenError()

        if result is TokenVerifyResult.EXPIRED:
            # Extract JTI from the expired token (skips expiry check)
            try:
                jti = get_token_jti(token)
            except JWTError:
                raise InvalidTokenError()

            # We don't have the full payload from an expired token, so we
            # can only blacklist the JTI — emit a minimal event with no user_id.
            if not await self.blacklisted_token_read.is_token_blacklisted(jti):
                # We cannot get exp from payload here, so use 0 epoch as sentinel
                # (the cleanup job will handle truly expired JTIs anyway).
                blacklisted_token = BlacklistedTokenModel(
                    jti=jti,
                    user_id="unknown",
                    expires_at=datetime.fromtimestamp(0, tz=timezone.utc),
                )
                await self.blacklisted_token_write.create_blacklisted_token(blacklisted_token)
            return

        # Token is VALID — normal logout path
        jti = payload["jti"]

        if await self.blacklisted_token_read.is_token_blacklisted(jti):
            return  # Already blacklisted — silently succeed

        blacklisted_token = BlacklistedTokenModel(
            jti=jti,
            user_id=payload["sub"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )

        await self.blacklisted_token_write.create_blacklisted_token(blacklisted_token)

        # Fix 10: typed event schema — payload is validated before publishing
        event = UserLoggedOutEvent(
            user_id=payload["sub"],
            jti=jti,
        )
        await self.event_bus.publish("user.logged_out", event.model_dump())
