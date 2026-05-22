from modules.auth.protocols import BlacklistedTokenWrite
from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel
class LogoutService():
    def __init__(
        self,
        blacklisted_token_write: BlacklistedTokenWrite
        ):
        self.blacklisted_token_write =blacklisted_token_write
        
    async def execute(self, data):
        
        blacklisted_token = BlacklistedTokenModel(
                jti= data["jti"],
                user_id= data["sub"]
        )
        
        self.blacklisted_token_write.create_blacklisted_token(blacklisted_token)
        