from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.db.motor import database
from core.exceptions.base import ForbiddenError
from core.security.jwt import verify_access_token
from modules.auth.adapters.mongo_token_blacklist_repository import MongoTokenBlacklistRepository
from modules.auth.exceptions import InvalidTokenError, TokenRevokedError

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db=Depends(database.get_database),
) -> dict:
    token = credentials.credentials

    payload = verify_access_token(token)

    if not payload:
        raise InvalidTokenError()

    jti = payload.get("jti")
    blacklist_repo = MongoTokenBlacklistRepository(db)

    if await blacklist_repo.is_token_blacklisted(jti):
        raise TokenRevokedError()

    return payload


CurrentUser = Annotated[dict, Depends(get_current_user)]