"""Unit tests for LoginService."""

import pytest

from modules.auth.services.login import LoginService
from modules.auth.schemas.login_request_schema import LoginRequest
from modules.auth.exceptions import InvalidCredentialsError, InactiveAccountError
from core.security.password import hash_password
from modules.users.model import UserModel
from uuid import uuid4

from tests.conftest import FakeUserRepository


def _make_repo(*, is_active: bool = True, password: str = "Passw0rd!") -> FakeUserRepository:
    repo = FakeUserRepository()
    user = UserModel(
        company_id=uuid4(),
        email="bob@example.com",
        hashed_password=hash_password(password),
        full_name="Bob",
        is_active=is_active,
    )
    repo._seed(user)
    return repo


@pytest.mark.asyncio
async def test_login_success():
    repo = _make_repo()
    service = LoginService(user_reader=repo)
    response = await service.execute(LoginRequest(email="bob@example.com", password="Passw0rd!"))

    assert response.email == "bob@example.com"
    assert response.access_token


@pytest.mark.asyncio
async def test_login_wrong_password():
    repo = _make_repo()
    service = LoginService(user_reader=repo)

    with pytest.raises(InvalidCredentialsError):
        await service.execute(LoginRequest(email="bob@example.com", password="WrongPass1"))


@pytest.mark.asyncio
async def test_login_unknown_email():
    repo = FakeUserRepository()  # empty
    service = LoginService(user_reader=repo)

    with pytest.raises(InvalidCredentialsError):
        await service.execute(LoginRequest(email="nobody@example.com", password="Passw0rd!"))


@pytest.mark.asyncio
async def test_login_inactive_account():
    repo = _make_repo(is_active=False)
    service = LoginService(user_reader=repo)

    with pytest.raises(InactiveAccountError):
        await service.execute(LoginRequest(email="bob@example.com", password="Passw0rd!"))


@pytest.mark.asyncio
async def test_login_missing_is_active_field_defaults_to_deny():
    """A user doc without is_active should be treated as inactive (fail closed)."""
    repo = FakeUserRepository()
    user = UserModel(
        company_id=uuid4(),
        email="ghost@example.com",
        hashed_password=hash_password("Passw0rd!"),
        full_name="Ghost",
        is_active=True,
    )
    repo._seed(user)
    # Simulate a doc with no is_active field (e.g. legacy data).
    doc = repo._store[str(user.id)]
    del doc["is_active"]

    service = LoginService(user_reader=repo)
    with pytest.raises(InactiveAccountError):
        await service.execute(LoginRequest(email="ghost@example.com", password="Passw0rd!"))
