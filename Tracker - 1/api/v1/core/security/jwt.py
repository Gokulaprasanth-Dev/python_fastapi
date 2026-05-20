from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, ExpiredSignatureError, jwt

from core.config.settings import get_settings

settings = get_settings()


def create_access_token(
    data: dict,
    expire_delta: timedelta | None,
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
        else timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    )

    to_encode.update({
        "iat": now,
        "exp": expire,
        "jti": str(uuid4()),
        "type": "access",
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        settings.jwt_algorithm,
    )

    return encoded_jwt


def verify_access_token(token: str):
    """
    Decode and validate an access token.

    Validation includes:
    - token signature verification
    - expiration check
    - required claim validation

    Required claims:
    - exp
    - sub

    Args:
        token: JWT access token string.

    Returns:
        Decoded token payload if valid.
        None if token is invalid or expired.
    """

    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require_exp": True,
                "require_sub": True,
            },
        )

    except ExpiredSignatureError:
        return None

    except JWTError:
        return None


def get_token_jti(token: str) -> str:
    """
    Extract the JTI claim from a token.

    Expiration validation is intentionally skipped
    so the JTI can still be retrieved from expired
    tokens during logout, revocation, or cleanup flows.

    Signature validation is still enforced.

    Args:
        token: JWT token string.

    Returns:
        Token JTI value.

    Raises:
        JWTError: If the token is invalid or missing
            the JTI claim.
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