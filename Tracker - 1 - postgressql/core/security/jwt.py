from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4

from jose import JWTError, ExpiredSignatureError, jwt

from core.config.settings import get_settings

settings = get_settings()


class TokenVerifyResult(str, Enum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"


def create_access_token(
    data: dict,
    expire_delta: timedelta | None = None,
) -> str:
    """
    Create and sign a JWT access token.

    The token includes:
    - exp  : expiration timestamp
    - iat  : issued-at timestamp
    - jti  : unique token identifier
    - type : token type identifier

    Args:
        data: Payload data to include in the token.
        expire_delta: Custom token lifetime. If not provided,
            the default access-token expiry from settings is used.

    Returns:
        Encoded JWT access token string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (
        expire_delta
        if expire_delta is not None
        else timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({
        "iat": now,
        "exp": expire,
        "jti": str(uuid4()),
        "type": "access",
    })
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key.get_secret_value(),
        settings.jwt_algorithm,
    )


def verify_access_token(token: str) -> tuple[TokenVerifyResult, dict | None]:
    """
    Decode and validate an access token.

    Returns a (result, payload) tuple so callers can distinguish between
    an expired token (safe to blacklist, allow logout) and an invalid one
    (reject immediately).

    Returns:
        (TokenVerifyResult.VALID, payload)   — token is good
        (TokenVerifyResult.EXPIRED, None)    — valid signature, past expiry
        (TokenVerifyResult.INVALID, None)    — bad signature / malformed / missing claims
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require_exp": True,
                "require_sub": True,
            },
        )
        return TokenVerifyResult.VALID, payload

    except ExpiredSignatureError:
        return TokenVerifyResult.EXPIRED, None

    except JWTError:
        return TokenVerifyResult.INVALID, None


def get_token_jti(token: str) -> str:
    """
    Extract the JTI claim from a token without checking expiry.

    Signature validation is still enforced.

    Args:
        token: JWT token string.

    Returns:
        Token JTI value.

    Raises:
        JWTError: If the token is invalid or missing the JTI claim.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={
            "verify_exp": False,
            "require_jti": True,
        },
    )
    return str(payload["jti"])
