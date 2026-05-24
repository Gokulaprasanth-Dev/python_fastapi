from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.postgres import get_db_session
from core.exceptions.base import ForbiddenError
from core.security.jwt import verify_access_token, TokenVerifyResult
from modules.auth.adapters.postgres_token_blacklist_repository import PostgresTokenBlacklistRepository
from modules.auth.exceptions import InvalidTokenError, TokenExpiredError, TokenRevokedError

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    token = credentials.credentials

    result, payload = verify_access_token(token)

    if result is TokenVerifyResult.EXPIRED:
        raise TokenExpiredError()

    if result is not TokenVerifyResult.VALID or payload is None:
        raise InvalidTokenError()

    jti = payload.get("jti")
    blacklist_repo = PostgresTokenBlacklistRepository(session)

    if await blacklist_repo.is_token_blacklisted(jti):
        raise TokenRevokedError()

    try:
        payload["sub"] = str(UUID(payload["sub"]))
    except (ValueError, AttributeError):
        raise InvalidTokenError()

    return payload


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    async def _check(current_user: CurrentUser) -> dict:
        if current_user.get("role") not in roles:
            raise ForbiddenError(
                "You do not have permission to perform this action",
                details={"required_roles": list(roles)},
            )
        return current_user
    return _check
