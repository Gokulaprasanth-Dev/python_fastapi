"""Unit tests for LogoutService — including the expired-token logout edge case."""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from core.security.jwt import create_access_token, TokenVerifyResult
from modules.auth.services.logout import LogoutService
from modules.auth.exceptions import InvalidTokenError
from core.events.event_bus import NoOpEventBus
from tests.conftest import FakeBlacklistRepository


def _make_service(blacklist: FakeBlacklistRepository) -> LogoutService:
    return LogoutService(
        blacklisted_token_write=blacklist,
        blacklisted_token_read=blacklist,
        event_bus=NoOpEventBus(),
    )


def _valid_token(user_id: str = "user-123") -> str:
    return create_access_token({"sub": user_id, "email": "a@b.com", "role": "user"})


def _expired_token(user_id: str = "user-123") -> str:
    return create_access_token(
        {"sub": user_id, "email": "a@b.com", "role": "user"},
        expire_delta=timedelta(seconds=-1),
    )


@pytest.mark.asyncio
async def test_logout_valid_token_blacklists_jti():
    blacklist = FakeBlacklistRepository()
    service = _make_service(blacklist)
    token = _valid_token()

    await service.execute(token)

    assert len(blacklist._blacklisted) == 1


@pytest.mark.asyncio
async def test_logout_already_blacklisted_is_idempotent():
    """Logging out twice with the same token must not raise an error."""
    blacklist = FakeBlacklistRepository()
    service = _make_service(blacklist)
    token = _valid_token()

    await service.execute(token)
    await service.execute(token)  # should not raise

    assert len(blacklist._blacklisted) == 1


@pytest.mark.asyncio
async def test_logout_expired_token_still_blacklists():
    """
    An expired token has a valid signature — the user must be able to logout
    even after their token has expired (to invalidate any replayed copies).
    """
    blacklist = FakeBlacklistRepository()
    service = _make_service(blacklist)
    token = _expired_token()

    await service.execute(token)

    assert len(blacklist._blacklisted) == 1


@pytest.mark.asyncio
async def test_logout_invalid_token_raises():
    blacklist = FakeBlacklistRepository()
    service = _make_service(blacklist)

    with pytest.raises(InvalidTokenError):
        await service.execute("this.is.garbage")
