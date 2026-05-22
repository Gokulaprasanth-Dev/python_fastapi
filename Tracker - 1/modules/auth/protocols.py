from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel

class BlacklistedTokenWrite():
    async def create_blacklisted_token(self,data: BlacklistedTokenModel): ...