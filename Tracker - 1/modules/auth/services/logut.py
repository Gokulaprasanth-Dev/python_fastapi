from modules.auth.protocols import BlacklistedTokenWrite
from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel

from core.security.jwt import verify_access_token
from modules.auth.exceptions import InvalidTokenError
class LogoutService():
    def __init__(
        self,
        blacklisted_token_write: BlacklistedTokenWrite
        ):
        self.blacklisted_token_write =blacklisted_token_write
        
    async def execute(self, token):
        
        payload=verify_access_token(token)
        
        if not payload:
            raise InvalidTokenError()
        
        blacklisted_token = BlacklistedTokenModel(
                jti= payload["jti"],
                user_id= payload["sub"]
        )
        
        await self.blacklisted_token_write.create_blacklisted_token(blacklisted_token)
        
        return {
            "message":" Logout is successful"
        }
        