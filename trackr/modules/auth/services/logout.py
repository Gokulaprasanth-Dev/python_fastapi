"""
LogoutService -- revokes the caller's JWT by blacklisting its jti.

Depends only on:
  - TokenBlacklist protocol
  - core/security/jwt.py for jti extraction

No FastAPI, no Motor, no HTTP concepts.
"""

from datetime import datetime, timezone

import jwt as pyjwt

from core.security.jwt import decode_access_token, extract_jti
from modules.auth.exceptions import InvalidTokenError, TokenExpiredError
from modules.auth.protocols import TokenBlacklist


class LogoutService:
    def __init__(self, blacklist: TokenBlacklist) -> None:
        self._blacklist = blacklist

    async def execute(self, token: str) -> None:
        """
        Validate the token, extract its jti and exp, then blacklist it.

        Raises:
            InvalidTokenError   -- token is malformed or signature invalid
            TokenExpiredError   -- token already expired (nothing to revoke)
        """
        try:
            payload = decode_access_token(token)
        except pyjwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except pyjwt.InvalidTokenError:
            raise InvalidTokenError()

        jti: str = payload["jti"]
        # exp comes back as a Unix timestamp (int) from PyJWT
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        await self._blacklist.add(jti=jti, expires_at=expires_at)
