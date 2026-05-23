"""
Shared test fixtures.

Provides lightweight in-memory fakes for repository protocols so unit
tests never touch MongoDB, S3, or the network.
"""

from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from modules.users.model import UserModel
from modules.companies.model import CompanyModel
from core.security.password import hash_password


# ── Fakes ──────────────────────────────────────────────────────────────────

class FakeUserRepository:
    """In-memory user store implementing UserReader + UserWriter protocols."""

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def _seed(self, user: UserModel) -> None:
        doc = user.model_dump(mode="json")
        doc["id"] = str(user.id)
        self._store[doc["id"]] = doc

    async def email_exist(self, email: str) -> bool:
        return any(u["email"] == email for u in self._store.values())

    async def get_user_by_email(self, email: str) -> dict | None:
        return next((u for u in self._store.values() if u["email"] == email), None)

    async def get_user_by_id(self, user_id: str) -> dict | None:
        return self._store.get(user_id)

    async def create_user(self, data: UserModel, session=None) -> str:
        doc = data.model_dump(mode="json")
        doc["id"] = str(data.id)
        self._store[doc["id"]] = doc
        return doc["id"]

    async def update_user(self, user_id: str, updates: dict, session=None) -> bool:
        if user_id not in self._store:
            return False
        self._store[user_id].update(updates)
        return True

    async def update_profile_image(self, user_id: str, url: str, session=None) -> bool:
        if user_id not in self._store:
            return False
        self._store[user_id]["profile_image_url"] = url
        return True

    async def soft_delete_user(self, user_id: str, session=None) -> bool:
        if user_id not in self._store:
            return False
        self._store[user_id]["is_active"] = False
        return True

    async def hard_delete_user(self, user_id: str, session=None) -> bool:
        return self._store.pop(user_id, None) is not None


class FakeCompanyRepository:
    """In-memory company store implementing CompanyWriter protocol."""

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    async def create_company(self, company: CompanyModel, session=None) -> str:
        doc = company.model_dump(mode="json")
        doc["id"] = str(company.id)
        self._store[doc["id"]] = doc
        return doc["id"]


class FakeBlacklistRepository:
    """In-memory token blacklist implementing both blacklist protocols."""

    def __init__(self) -> None:
        self._blacklisted: set[str] = set()

    async def is_token_blacklisted(self, jti: str) -> bool:
        return jti in self._blacklisted

    async def create_blacklisted_token(self, data) -> str:
        self._blacklisted.add(data.jti)
        return str(data.id)


class FakeStorage:
    """In-memory storage stub implementing StorageProtocol."""

    def __init__(self) -> None:
        self.uploaded: dict[str, bytes] = {}
        self.deleted: list[str] = []

    async def upload_file(self, file_bytes: bytes, key: str, content_type: str) -> str:
        self.uploaded[key] = file_bytes
        return f"https://fake-s3.example.com/{key}"

    async def delete_file(self, key: str) -> None:
        self.deleted.append(key)
        self.uploaded.pop(key, None)


class FakeUnitOfWork:
    """No-op UoW for unit tests — no transactions needed."""

    def __init__(self) -> None:
        self.session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def company_repo() -> FakeCompanyRepository:
    return FakeCompanyRepository()


@pytest.fixture
def blacklist_repo() -> FakeBlacklistRepository:
    return FakeBlacklistRepository()


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def existing_user(user_repo: FakeUserRepository) -> dict:
    """Seed an active, verified user into the fake repo and return the doc."""
    user = UserModel(
        company_id=uuid4(),
        email="alice@example.com",
        hashed_password=hash_password("Passw0rd!"),
        full_name="Alice Example",
        role="user",
        is_active=True,
        is_verified=True,
    )
    user_repo._seed(user)
    return user_repo._store[str(user.id)]
