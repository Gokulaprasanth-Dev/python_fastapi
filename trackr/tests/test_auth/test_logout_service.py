"""
Unit tests for LogoutService.

Uses a fake in-memory TokenBlacklist -- no FastAPI, no Motor, no network.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.security.jwt import create_access_token
from modules.auth.exceptions import InvalidTokenError, TokenExpiredError
from modules.auth.services.logout import LogoutService


# ---------------------------------------------------------------------------
# Fake blacklist
# ---------------------------------------------------------------------------


class FakeTokenBlacklist:
    def __init__(self) -> None:
        self.revoked: dict[str, datetime] = {}

    async def add(self, jti: str, expires_at: datetime) -> None:
        self.revoked[jti] = expires_at

    async def is_revoked(self, jti: str) -> bool:
        return jti in self.revoked


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_token() -> str:
    return create_access_token(user_id=uuid4(), email="alice@acme.com")


def make_service(blacklist: FakeTokenBlacklist | None = None) -> tuple[LogoutService, FakeTokenBlacklist]:
    bl = blacklist or FakeTokenBlacklist()
    return LogoutService(blacklist=bl), bl


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_logout_adds_jti_to_blacklist() -> None:
    service, blacklist = make_service()
    token = make_token()

    await service.execute(token)

    assert len(blacklist.revoked) == 1


@pytest.mark.asyncio
async def test_logout_blacklisted_jti_has_future_expiry() -> None:
    service, blacklist = make_service()
    token = make_token()

    await service.execute(token)

    expires_at = list(blacklist.revoked.values())[0]
    assert expires_at > datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_logout_twice_does_not_raise() -> None:
    """Idempotent -- blacklisting the same token twice is safe."""
    service, blacklist = make_service()
    token = make_token()

    await service.execute(token)
    await service.execute(token)  # should not raise

    # Still only one entry (upsert semantics)
    assert len(blacklist.revoked) == 1


@pytest.mark.asyncio
async def test_logout_invalid_token_raises() -> None:
    service, _ = make_service()

    with pytest.raises(InvalidTokenError):
        await service.execute("not.a.valid.token")


@pytest.mark.asyncio
async def test_logout_expired_token_raises() -> None:
    """
    Expired tokens should not be accepted for logout --
    they can no longer be used anyway.
    """
    import jwt as pyjwt
    from datetime import timedelta
    from core.config.settings import get_settings

    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "email": "alice@acme.com",
        "jti": str(uuid4()),
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),  # already expired
    }
    expired_token = pyjwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    service, _ = make_service()
    with pytest.raises(TokenExpiredError):
        await service.execute(expired_token)


@pytest.mark.asyncio
async def test_logout_different_tokens_get_different_jtis() -> None:
    """Each token issued gets its own jti -- two logouts = two blacklist entries."""
    service, blacklist = make_service()

    token_a = make_token()
    token_b = make_token()

    await service.execute(token_a)
    await service.execute(token_b)

    assert len(blacklist.revoked) == 2
