"""
Unit tests for LoginService.

Uses a fake in-memory UserReader — no FastAPI, no Motor, no network.
"""

from uuid import uuid4

import pytest

from core.security.password import hash_password
from modules.auth.exceptions import InvalidCredentialsError
from modules.auth.schemas.requests import LoginRequest
from modules.auth.services.login import LoginService
from modules.users.models import UserDocument


# ---------------------------------------------------------------------------
# Fake adapter
# ---------------------------------------------------------------------------


class FakeUserReader:
    def __init__(self, users: list[UserDocument] | None = None) -> None:
        self._users = {u.email: u for u in (users or [])}

    async def email_exists(self, email: str) -> bool:
        return email in self._users

    async def get_by_email(self, email: str) -> UserDocument | None:
        return self._users.get(email)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_user(**overrides) -> UserDocument:
    company_id = uuid4()
    defaults = dict(
        full_name="Alice Admin",
        email="alice@acme.com",
        hashed_password=hash_password("supersecret"),
        phone="+919876543210",
        company_id=company_id,
        role="admin",
        is_active=True,
    )
    return UserDocument(**{**defaults, **overrides})


def make_request(**overrides) -> LoginRequest:
    defaults = dict(email="alice@acme.com", password="supersecret")
    return LoginRequest(**{**defaults, **overrides})


def make_service(users: list[UserDocument] | None = None) -> LoginService:
    return LoginService(user_reader=FakeUserReader(users))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_returns_access_token() -> None:
    user = make_user()
    service = make_service([user])

    response = await service.execute(make_request())

    assert response.access_token
    assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_response_contains_user_info() -> None:
    user = make_user()
    service = make_service([user])

    response = await service.execute(make_request())

    assert response.user_id == user.id
    assert response.email == user.email
    assert response.full_name == user.full_name
    assert response.company_id == user.company_id


@pytest.mark.asyncio
async def test_login_token_is_valid_jwt() -> None:
    import jwt as pyjwt
    from core.config.settings import get_settings

    user = make_user()
    service = make_service([user])
    response = await service.execute(make_request())

    settings = get_settings()
    payload = pyjwt.decode(
        response.access_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(user.id)
    assert payload["email"] == user.email


@pytest.mark.asyncio
async def test_login_wrong_email_raises_invalid_credentials() -> None:
    service = make_service([make_user()])

    with pytest.raises(InvalidCredentialsError):
        await service.execute(make_request(email="nobody@acme.com"))


@pytest.mark.asyncio
async def test_login_wrong_password_raises_invalid_credentials() -> None:
    service = make_service([make_user()])

    with pytest.raises(InvalidCredentialsError):
        await service.execute(make_request(password="wrongpassword"))


@pytest.mark.asyncio
async def test_login_inactive_user_raises_invalid_credentials() -> None:
    user = make_user(is_active=False)
    service = make_service([user])

    with pytest.raises(InvalidCredentialsError):
        await service.execute(make_request())


@pytest.mark.asyncio
async def test_login_error_message_is_vague() -> None:
    """Ensure we never reveal whether email or password was wrong."""
    service = make_service([make_user()])

    try:
        await service.execute(make_request(email="ghost@acme.com"))
    except InvalidCredentialsError as exc:
        assert "email" in str(exc).lower() or "password" in str(exc).lower()
        assert "not found" not in str(exc).lower()
        assert "does not exist" not in str(exc).lower()
