"""
auth/dependencies.py -- FastAPI dependencies for authenticated routes.

get_current_user is the single dependency all protected routes use.
It lives here (not in services/) because it uses Depends() and HTTPException,
which must never appear below the router layer.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

import jwt as pyjwt

from core.db.motor import get_db
from core.security.jwt import decode_access_token
from modules.auth.adapters.mongo import MongoTokenBlacklistAdapter

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncIOMotorDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> dict:
    """
    Decode and validate the Bearer token from the Authorization header.

    Returns the decoded JWT payload dict on success.

    Raises HTTP 401 for:
      - Missing / malformed Authorization header        (HTTPBearer handles this)
      - Expired token
      - Invalid signature or malformed token
      - Revoked token (present in token_blacklist)
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Blacklist check — O(1) indexed lookup on _id
    blacklist = MongoTokenBlacklistAdapter(db)
    if await blacklist.is_revoked(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
