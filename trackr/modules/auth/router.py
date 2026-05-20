"""
auth/router.py -- the ONLY file in this module that knows about FastAPI.

Responsibilities:
  - Declare HTTP routes
  - Wire concrete adapters into services via Depends()
  - Translate DomainErrors to HTTP responses (via registered handlers in core/)

Everything below this layer is plain Python.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.db.motor import get_db
from modules.auth.adapters.mongo import MongoTokenBlacklistAdapter
from modules.auth.dependencies import get_current_user
from modules.auth.schemas.requests import LoginRequest
from modules.auth.schemas.responses import LoginResponse
from modules.auth.services.login import LoginService
from modules.auth.services.logout import LogoutService
from modules.companies.adapters.mongo import MongoCompanyAdapter
from modules.users.adapters.mongo import MongoUserAdapter
from modules.users.schemas.requests import RegisterRequest
from modules.users.schemas.responses import RegisterResponse
from modules.users.services.register import RegisterService

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new company and its first admin user",
)
async def register(
    data: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> RegisterResponse:
    user_adapter = MongoUserAdapter(db)
    company_adapter = MongoCompanyAdapter(db)
    service = RegisterService(
        user_reader=user_adapter,
        user_writer=user_adapter,
        company_writer=company_adapter,
    )
    return await service.execute(data)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive a JWT access token",
)
async def login(
    data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> LoginResponse:
    user_adapter = MongoUserAdapter(db)
    service = LoginService(user_reader=user_adapter)
    return await service.execute(data)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke the current access token",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncIOMotorDatabase = Depends(get_db),  # type: ignore[type-arg]
    _current_user: dict = Depends(get_current_user),  # validates token first
) -> None:
    """
    Blacklists the Bearer token so it cannot be used again.

    The token must be valid and non-expired. Returns 204 No Content on success.
    Subsequent requests with the same token will receive 401 Token has been revoked.
    """
    blacklist_adapter = MongoTokenBlacklistAdapter(db)
    service = LogoutService(blacklist=blacklist_adapter)
    await service.execute(credentials.credentials)
