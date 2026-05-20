"""
Unit tests for RegisterService.

Uses fake in-memory adapters — no FastAPI, no Motor, no network.
Tests the service logic in complete isolation.
"""

import pytest

from modules.companies.models import CompanyDocument
from modules.users.exceptions import EmailAlreadyExistsError
from modules.users.models import UserDocument
from modules.users.schemas.requests import RegisterRequest
from modules.users.services.register import RegisterService


# ---------------------------------------------------------------------------
# Fake adapters
# ---------------------------------------------------------------------------


class FakeUserAdapter:
    """In-memory implementation of UserReader + UserWriter protocols."""

    def __init__(self, existing_emails: set[str] | None = None) -> None:
        self.inserted: list[UserDocument] = []
        self._emails: set[str] = existing_emails or set()

    async def email_exists(self, email: str) -> bool:
        return email in self._emails

    async def insert(self, user: UserDocument) -> None:
        self._emails.add(user.email)
        self.inserted.append(user)


class FakeCompanyAdapter:
    """In-memory implementation of CompanyWriter protocol."""

    def __init__(self) -> None:
        self.inserted: list[CompanyDocument] = []

    async def insert(self, company: CompanyDocument) -> None:
        self.inserted.append(company)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_request(**overrides) -> RegisterRequest:  # type: ignore[return]
    defaults = {
        "company_name": "Acme Corp",
        "company_country": "India",
        "company_industry": "logistics",   # CompanyIndustry enum value
        "full_name": "Alice Admin",
        "email": "alice@acme.com",
        "password": "supersecret",
        "phone": "+919876543210",
    }
    return RegisterRequest(**{**defaults, **overrides})


def make_service(
    existing_emails: set[str] | None = None,
) -> tuple[RegisterService, FakeUserAdapter, FakeCompanyAdapter]:
    user_adapter = FakeUserAdapter(existing_emails)
    company_adapter = FakeCompanyAdapter()
    service = RegisterService(
        user_reader=user_adapter,
        user_writer=user_adapter,
        company_writer=company_adapter,
    )
    return service, user_adapter, company_adapter


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_creates_company_and_user() -> None:
    service, user_adapter, company_adapter = make_service()
    request = make_request()

    response = await service.execute(request)

    assert response.email == "alice@acme.com"
    assert response.full_name == "Alice Admin"
    assert response.company_name == "Acme Corp"
    assert len(user_adapter.inserted) == 1
    assert len(company_adapter.inserted) == 1


@pytest.mark.asyncio
async def test_register_links_user_to_company() -> None:
    service, user_adapter, company_adapter = make_service()
    request = make_request()

    response = await service.execute(request)

    assert response.user_id == user_adapter.inserted[0].id
    assert response.company_id == company_adapter.inserted[0].id
    assert user_adapter.inserted[0].company_id == company_adapter.inserted[0].id


@pytest.mark.asyncio
async def test_register_hashes_password() -> None:
    service, user_adapter, _ = make_service()
    request = make_request(password="supersecret")

    await service.execute(request)

    stored = user_adapter.inserted[0]
    assert stored.hashed_password != "supersecret"
    assert stored.hashed_password.startswith("$2b$")


@pytest.mark.asyncio
async def test_register_raises_on_duplicate_email() -> None:
    service, _, _ = make_service(existing_emails={"alice@acme.com"})
    request = make_request(email="alice@acme.com")

    with pytest.raises(EmailAlreadyExistsError):
        await service.execute(request)


@pytest.mark.asyncio
async def test_register_does_not_insert_on_duplicate_email() -> None:
    service, user_adapter, company_adapter = make_service(
        existing_emails={"alice@acme.com"}
    )
    request = make_request(email="alice@acme.com")

    try:
        await service.execute(request)
    except EmailAlreadyExistsError:
        pass

    # Neither company nor user should have been persisted
    assert len(user_adapter.inserted) == 0
    assert len(company_adapter.inserted) == 0


@pytest.mark.asyncio
async def test_register_assigns_admin_role() -> None:
    service, user_adapter, _ = make_service()

    await service.execute(make_request())

    assert user_adapter.inserted[0].role == "admin"


@pytest.mark.asyncio
async def test_register_user_is_active_by_default() -> None:
    service, user_adapter, _ = make_service()

    await service.execute(make_request())

    assert user_adapter.inserted[0].is_active is True
