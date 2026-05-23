from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.db.motor import database
from core.uow.mongo_unit_of_work import MongoUnitOfWork  # FIX #4: UoW
from core.events.event_bus import NoOpEventBus           # FIX #11: EventBus

from modules.users.adapters.mongo_user_repository import MongoUserRepository
from modules.companies.adapters.mongo_company_repository import MongoCompanyRepository  # FIX #7: adapters not adopters

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


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
) -> RegisterResponse:
    user_repository = MongoUserRepository(db)
    company_repository = MongoCompanyRepository(db)

    # FIX #4: pass UoW so register service can wrap both writes in a transaction
    uow = MongoUnitOfWork(database.get_client())

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
async def login(
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

    # FIX #11: inject event bus — no-op today, swap later for real broker
    service = LogoutService(
        blacklisted_token_write=token_blacklist_repository,
        blacklisted_token_read=token_blacklist_repository,
        event_bus=NoOpEventBus(),
    )
    await service.execute(credentials.credentials)