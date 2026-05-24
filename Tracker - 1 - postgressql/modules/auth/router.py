from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.postgres import get_db_session
from core.events.event_bus import NoOpEventBus
from core.middleware.rate_limit import limiter
from core.uow.postgres_unit_of_work import PostgresUnitOfWork, UnitOfWork
from core.db.postgres import database

from modules.users.adapters.postgres_user_repository import PostgresUserRepository
from modules.companies.adapters.postgres_company_repository import PostgresCompanyRepository

from modules.auth.schemas.register_request_schema import RegisterRequest
from modules.auth.schemas.register_response_schema import RegisterResponse
from modules.auth.services.register import RegisterService

from modules.auth.schemas.login_request_schema import LoginRequest
from modules.auth.schemas.login_response_schema import LoginResponse
from modules.auth.services.login import LoginService

from modules.auth.adapters.postgres_token_blacklist_repository import PostgresTokenBlacklistRepository
from modules.auth.services.logout import LogoutService


router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer()


def get_uow(session: AsyncSession = Depends(get_db_session)) -> UnitOfWork:
    return PostgresUnitOfWork(database.get_session_factory())


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
    uow: UnitOfWork = Depends(get_uow),
) -> RegisterResponse:
    user_repository = PostgresUserRepository(session)
    company_repository = PostgresCompanyRepository(session)
    service = RegisterService(
        user_reader=user_repository,
        user_writer=user_repository,
        company_writer=company_repository,
        uow=uow,
    )
    return await service.execute(data)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    user_repository = PostgresUserRepository(session)
    service = LoginService(user_reader=user_repository)
    return await service.execute(data)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    token_blacklist_repository = PostgresTokenBlacklistRepository(session)
    service = LogoutService(
        blacklisted_token_write=token_blacklist_repository,
        blacklisted_token_read=token_blacklist_repository,
        event_bus=NoOpEventBus(),
    )
    await service.execute(credentials.credentials)
