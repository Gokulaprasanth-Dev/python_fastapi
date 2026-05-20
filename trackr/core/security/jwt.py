from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from jose import JWTError, ExpiredSignatureError, jwt

from core.config.settings import get_settings

settings = get_settings()


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Return a signed JWT access token for the given user.

    Every token gets a unique `jti` (JWT ID) so it can be individually
    revoked by inserting that jti into the token blacklist on logout.
    """

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Raises:
        ExpiredSignatureError -- token expired
        JWTError              -- invalid token/signature
    """

    return jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )


def extract_jti(token: str) -> str:
    """
    Decode token without verifying expiry and extract JTI.

    Signature validation is still enforced.
    """

    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": False},
    )

    jti = payload.get("jti")

    if not jti:
        raise JWTError("Missing jti claim")

    return str(jti)