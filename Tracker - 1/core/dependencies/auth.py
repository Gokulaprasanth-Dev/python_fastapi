from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.db.motor import database
from core.exceptions.base import ForbiddenError
from core.security.jwt import verify_access_token, TokenVerifyResult
from modules.auth.adapters.mongo_token_blacklist_repository import MongoTokenBlacklistRepository
from modules.auth.exceptions import InvalidTokenError, TokenExpiredError, TokenRevokedError

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db=Depends(database.get_database),
) -> dict:
    token = credentials.credentials

    result, payload = verify_access_token(token)

    # Fix 8: distinguish expired vs invalid — expired still has a valid
    # signature so it's meaningful to tell the client why it was rejected.
    if result is TokenVerifyResult.EXPIRED:
        raise TokenExpiredError()

    if result is not TokenVerifyResult.VALID or payload is None:
        raise InvalidTokenError()

    jti = payload.get("jti")
    blacklist_repo = MongoTokenBlacklistRepository(db)

    if await blacklist_repo.is_token_blacklisted(jti):
        raise TokenRevokedError()

    # Fix 6: normalise sub to a canonical UUID string so path-parameter
    # comparisons (current_user["sub"] == user_id) are format-safe.
    try:
        payload["sub"] = str(UUID(payload["sub"]))
    except (ValueError, AttributeError):
        raise InvalidTokenError()

    return payload


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    """
    Dependency factory that enforces role-based access control.

    Usage:
        @router.delete("/{user_id}/hard", dependencies=[Depends(require_role("admin"))])
    """
    async def _check(current_user: CurrentUser) -> dict:
        if current_user.get("role") not in roles:
            raise ForbiddenError(
                "You do not have permission to perform this action",
                details={"required_roles": list(roles)},
            )
        return current_user
    return _check
