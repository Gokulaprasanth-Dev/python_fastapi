from modules.auth.protocols import BlacklistedTokenWrite
class LogoutService():
    def __init__(
        self,
        blacklisted_token_write: BlacklistedTokenWrite
        ):
        self.blacklisted_token_write =blacklisted_token_write
        
    async def execute():