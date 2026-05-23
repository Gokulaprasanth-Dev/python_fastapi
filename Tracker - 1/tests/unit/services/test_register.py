"""Unit tests for RegisterService."""

import pytest

from modules.auth.services.register import RegisterService
from modules.auth.schemas.register_request_schema import RegisterRequest
from modules.auth.exceptions import EmailAlreadyExistsError
from tests.conftest import FakeUserRepository, FakeCompanyRepository, FakeUnitOfWork


def _make_service(user_repo=None, company_repo=None, uow=None) -> RegisterService:
    return RegisterService(
        user_reader=user_repo or FakeUserRepository(),
        user_writer=user_repo or FakeUserRepository(),
        company_writer=company_repo or FakeCompanyRepository(),
        uow=uow or FakeUnitOfWork(),
    )


def _request(**overrides) -> RegisterRequest:
    defaults = dict(
        company_name="Acme Corp",
        company_country="US",
        company_industry="Tech",
        full_name="Jane Doe",
        email="jane@acme.com",
        password="Passw0rd!",
        phone="+14155552671",
    )
    return RegisterRequest(**{**defaults, **overrides})


@pytest.mark.asyncio
async def test_register_success():
    user_repo = FakeUserRepository()
    company_repo = FakeCompanyRepository()
    service = _make_service(user_repo=user_repo, company_repo=company_repo)

    response = await service.execute(_request())

    assert response.email == "jane@acme.com"
    assert response.company_name == "Acme Corp"
    assert len(user_repo._store) == 1
    assert len(company_repo._store) == 1


@pytest.mark.asyncio
async def test_register_duplicate_email_raises():
    user_repo = FakeUserRepository()
    company_repo = FakeCompanyRepository()
    service = _make_service(user_repo=user_repo, company_repo=company_repo)

    await service.execute(_request())

    with pytest.raises(EmailAlreadyExistsError):
        await service.execute(_request())


@pytest.mark.asyncio
async def test_register_password_is_hashed():
    user_repo = FakeUserRepository()
    service = _make_service(user_repo=user_repo)

    await service.execute(_request(password="MySecret1"))

    stored = next(iter(user_repo._store.values()))
    assert stored["hashed_password"] != "MySecret1"
    assert stored["hashed_password"].startswith("$")


@pytest.mark.asyncio
async def test_register_noop_uow_still_creates_records():
    """NoOpUnitOfWork fallback path (standalone mongod) must still work."""
    user_repo = FakeUserRepository()
    company_repo = FakeCompanyRepository()
    service = _make_service(
        user_repo=user_repo,
        company_repo=company_repo,
        uow=FakeUnitOfWork(),
    )

    response = await service.execute(_request())
    assert response.user_id is not None
