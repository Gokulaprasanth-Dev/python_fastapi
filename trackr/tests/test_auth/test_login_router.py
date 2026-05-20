"""
Integration tests for POST /api/v1/auth/login.

Uses a fake in-memory DB — no real MongoDB required.
Registers a user first via the /register endpoint, then logs in.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from core.security.password import hash_password


# ---------------------------------------------------------------------------
# Fake DB (same pattern as register router tests)
# ---------------------------------------------------------------------------


class FakeCollection:
    def __init__(self) -> None:
        self._docs: list[dict] = []

    async def find_one(self, query: dict, projection: dict | None = None) -> dict | None:
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    async def insert_one(self, document: dict) -> None:
        self._docs.append(document)


class FakeDB:
    def __init__(self) -> None:
        self._cols: dict[str, FakeCollection] = {}

    def __getitem__(self, name: str) -> FakeCollection:
        if name not in self._cols:
            self._cols[name] = FakeCollection()
        return self._cols[name]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def http_client():
    from main import create_app
    from core.db.motor import get_db

    fake_db = FakeDB()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: fake_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac, fake_db


REGISTER_PAYLOAD = {
    "company_name": "Acme Corp",
    "company_country": "India",
    "company_industry": "logistics",
    "full_name": "Alice Admin",
    "email": "alice@acme.com",
    "password": "supersecret",
    "phone": "+919876543210",
}

LOGIN_PAYLOAD = {
    "email": "alice@acme.com",
    "password": "supersecret",
}


async def registered_client(http_client):
    """Register a user and return the client + fake_db."""
    client, fake_db = http_client
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    return client, fake_db


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_returns_200(http_client) -> None:
    client, _ = await registered_client(http_client)
    response = await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_response_contains_token(http_client) -> None:
    client, _ = await registered_client(http_client)
    body = (await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)).json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


@pytest.mark.asyncio
async def test_login_response_contains_user_info(http_client) -> None:
    client, _ = await registered_client(http_client)
    body = (await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)).json()

    assert body["email"] == "alice@acme.com"
    assert body["full_name"] == "Alice Admin"
    assert "user_id" in body
    assert "company_id" in body


@pytest.mark.asyncio
async def test_login_does_not_expose_password(http_client) -> None:
    client, _ = await registered_client(http_client)
    body = (await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)).json()

    assert "password" not in body
    assert "hashed_password" not in body


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(http_client) -> None:
    client, _ = await registered_client(http_client)
    response = await client.post(
        "/api/v1/auth/login",
        json={**LOGIN_PAYLOAD, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(http_client) -> None:
    client, _ = http_client
    response = await client.post(
        "/api/v1/auth/login",
        json={**LOGIN_PAYLOAD, "email": "ghost@acme.com"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_email_format_returns_422(http_client) -> None:
    client, _ = http_client
    response = await client.post(
        "/api/v1/auth/login",
        json={**LOGIN_PAYLOAD, "email": "not-an-email"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_token_is_decodable_jwt(http_client) -> None:
    import jwt as pyjwt
    from core.config.settings import get_settings

    client, _ = await registered_client(http_client)
    body = (await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)).json()

    settings = get_settings()
    payload = pyjwt.decode(
        body["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["email"] == "alice@acme.com"
    assert "sub" in payload
    assert "exp" in payload
