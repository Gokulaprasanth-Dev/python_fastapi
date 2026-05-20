"""
Integration tests for POST /api/v1/auth/register.

Uses a fake in-memory DB override — no real MongoDB required.
Tests the full HTTP stack: request parsing → router → service → response.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from modules.companies.models import CompanyDocument
from modules.users.models import UserDocument


# ---------------------------------------------------------------------------
# In-memory DB fake and app override
# ---------------------------------------------------------------------------


class FakeDB:
    """Minimal fake that mimics AsyncIOMotorDatabase enough for adapters."""

    def __init__(self) -> None:
        self._collections: dict[str, "FakeCollection"] = {}

    def __getitem__(self, name: str) -> "FakeCollection":
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]


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

    def all(self) -> list[dict]:
        return self._docs


@pytest_asyncio.fixture
async def app_with_fake_db():
    from main import create_app
    from core.db.motor import get_db

    fake_db = FakeDB()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: fake_db
    return app, fake_db


@pytest_asyncio.fixture
async def http_client(app_with_fake_db):
    app, fake_db = app_with_fake_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac, fake_db


# ---------------------------------------------------------------------------
# Valid payload fixture
# ---------------------------------------------------------------------------


VALID_PAYLOAD = {
    "company_name": "Acme Corp",
    "company_country": "India",
    "company_industry": "logistics",   # CompanyIndustry enum value
    "full_name": "Alice Admin",
    "email": "alice@acme.com",
    "password": "supersecret",
    "phone": "+919876543210",           # E.164 format
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_returns_201(http_client) -> None:
    client, _ = http_client
    response = await client.post("/api/v1/auth/register", json=VALID_PAYLOAD)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_response_shape(http_client) -> None:
    client, _ = http_client
    response = await client.post("/api/v1/auth/register", json=VALID_PAYLOAD)
    body = response.json()

    assert "user_id" in body
    assert "company_id" in body
    assert body["email"] == "alice@acme.com"
    assert body["full_name"] == "Alice Admin"
    assert body["company_name"] == "Acme Corp"


@pytest.mark.asyncio
async def test_register_does_not_expose_password(http_client) -> None:
    client, _ = http_client
    response = await client.post("/api/v1/auth/register", json=VALID_PAYLOAD)
    body = response.json()

    assert "password" not in body
    assert "hashed_password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(http_client) -> None:
    client, _ = http_client
    await client.post("/api/v1/auth/register", json=VALID_PAYLOAD)
    response = await client.post("/api/v1/auth/register", json=VALID_PAYLOAD)

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_short_password_returns_422(http_client) -> None:
    client, _ = http_client
    payload = {**VALID_PAYLOAD, "password": "short"}
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(http_client) -> None:
    client, _ = http_client
    payload = {**VALID_PAYLOAD, "email": "not-an-email"}
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_field_returns_422(http_client) -> None:
    client, _ = http_client
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "company_name"}
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_phone_returns_422(http_client) -> None:
    client, _ = http_client
    payload = {**VALID_PAYLOAD, "phone": "09876543210"}  # missing + prefix
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_industry_returns_422(http_client) -> None:
    client, _ = http_client
    payload = {**VALID_PAYLOAD, "company_industry": "not_a_real_industry"}
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422
