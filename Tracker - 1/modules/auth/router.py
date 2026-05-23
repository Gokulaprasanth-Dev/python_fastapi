from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config.dependencies import AppSettings
from core.config.settings import Settings
from core.db.motor import database
from core.events.event_bus import NoOpEventBus
from core.middleware.rate_limit import limiter
from core.uow.mongo_unit_of_work import MongoUnitOfWork, NoOpUnitOfWork, UnitOfWork

from modules.users.adapters.mongo_user_repository import MongoUserRepository
from modules.companies.adapters.mongo_company_repository import MongoCompanyRepository

from modules.auth.schemas.register_request_schema import RegisterRequest
from modules.auth.schemas.register_response_schema import RegisterResponse
from modules.auth.services.register import RegisterService

from modules.auth.schemas.login_request_schema import LoginRequest
from modules.auth.schemas.login_response_schema import LoginResponse
from modules.auth.services.login import LoginService

from modules.auth.adapters.mongo_token_blacklist_repository import MongoTokenBlacklistRepository
from modules.auth.services.logout import LogoutService


router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer()


def get_uow(settings: AppSettings) -> UnitOfWork:
    """
    FastAPI dependency that returns the appropriate Unit of Work.

    Settings is now injected explicitly so the dependency graph is visible
    and this function is easy to override in tests.
    """
    if settings.mongo_transactions_enabled:
        return MongoUnitOfWork(database.get_client())
    return NoOpUnitOfWork()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
    uow: UnitOfWork = Depends(get_uow),
) -> RegisterResponse:
    user_repository = MongoUserRepository(db)
    company_repository = MongoCompanyRepository(db)
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
    db: AsyncIOMotorDatabase = Depends(database.get_database),
) -> LoginResponse:
    user_repository = MongoUserRepository(db)
    service = LoginService(user_reader=user_repository)
    return await service.execute(data)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncIOMotorDatabase = Depends(database.get_database),
) -> None:
    token_blacklist_repository = MongoTokenBlacklistRepository(db)
    service = LogoutService(
        blacklisted_token_write=token_blacklist_repository,
        blacklisted_token_read=token_blacklist_repository,
        event_bus=NoOpEventBus(),
    )
    await service.execute(credentials.credentials)
