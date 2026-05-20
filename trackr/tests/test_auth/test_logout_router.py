"""
Integration tests for POST /api/v1/auth/logout.

Full HTTP stack with fake in-memory DB.
Register -> Login -> Logout -> verify token is dead.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ---------------------------------------------------------------------------
# Fake DB (same pattern as other router tests)
# ---------------------------------------------------------------------------


class FakeCollection:
    def __init__(self) -> None:
        self._docs: list[dict] = []

    async def find_one(self, query: dict, projection: dict | None = None) -> dict | None:
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    async def update_one(
        self, query: dict, update: dict, upsert: bool = False
    ) -> None:
        """Minimal upsert -- used by the blacklist adapter."""
        existing = await self.find_one(query)
        if existing is None and upsert:
            doc = {"_id": query["_id"]}
            doc.update(update.get("$setOnInsert", {}))
            self._docs.append(doc)

    async def insert_one(self, document: dict) -> None:
        self._docs.append(document)

    async def create_index(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        pass  # no-op in tests


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

LOGIN_PAYLOAD = {"email": "alice@acme.com", "password": "supersecret"}


async def login_token(client: AsyncClient) -> str:
    """Register + login and return the access token."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_logout_returns_204(http_client) -> None:
    client, _ = http_client
    token = await login_token(client)

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_response_has_no_body(http_client) -> None:
    client, _ = http_client
    token = await login_token(client)

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.content == b""


@pytest.mark.asyncio
async def test_token_rejected_after_logout(http_client) -> None:
    """
    Core blacklist contract: a token that was valid before logout
    must be rejected with 401 afterward.
    """
    client, _ = http_client
    token = await login_token(client)

    # Logout
    await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Second logout with same token must fail
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert "revoked" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_without_token_returns_403(http_client) -> None:
    """HTTPBearer returns 401 when Authorization header is missing."""
    client, _ = http_client

    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_with_invalid_token_returns_401(http_client) -> None:
    client, _ = http_client

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer this.is.garbage"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_new_token_works_after_previous_logout(http_client) -> None:
    """
    Blacklist is per-jti. A fresh login issues a new token with a new jti
    -- it must still be accepted even if a previous token was revoked.
    """
    client, _ = http_client

    token_a = await login_token(client)
    await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Log in again -- new token, new jti
    resp = await client.post("/api/v1/auth/login", json=LOGIN_PAYLOAD)
    token_b = resp.json()["access_token"]

    # token_b should still be valid -- log out cleanly
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 204
