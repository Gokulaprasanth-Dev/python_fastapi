from modules.auth.protocols import BlacklistedTokenWrite, BlacklistedTokenRead

from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel

from core.security.jwt import verify_access_token
from modules.auth.exceptions import InvalidTokenError

from datetime import datetime, timezone
class LogoutService():
    def __init__(
        self,
        blacklisted_token_write: BlacklistedTokenWrite,
        blacklisted_token_read: BlacklistedTokenRead
        ):
        self.blacklisted_token_write =blacklisted_token_write
        self.blacklisted_token_read =blacklisted_token_read
        
    async def execute(self, token):
        
        payload=verify_access_token(token)
        
        if not payload:
            raise InvalidTokenError()
        jti = payload["jti"]

        # Already blacklisted — silently succeed
        if await self.blacklisted_token_read.is_token_blacklisted(jti):
            return
        
        blacklisted_token = BlacklistedTokenModel(
                jti= jti,
                user_id= payload["sub"],
                expires_at= datetime.fromtimestamp(payload["exp"],tz= timezone.utc)
        )
        
        await self.blacklisted_token_write.create_blacklisted_token(blacklisted_token)