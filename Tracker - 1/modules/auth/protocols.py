from typing import Protocol
from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel

class BlacklistedTokenWrite(Protocol):
    async def create_blacklisted_token(self,data: BlacklistedTokenModel): ...