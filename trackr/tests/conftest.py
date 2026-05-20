"""
Shared pytest fixtures.

The AsyncClient uses ASGI transport — no real network, no real MongoDB.
Individual test modules override get_db() with fake in-memory adapters.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import create_app


@pytest_asyncio.fixture
async def client():
    """
    Bare async HTTP client against the app.
    Tests that need DB isolation should override get_db() via app.dependency_overrides.
    """
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
