from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.auth.schemas.register_response_schema import RegisterResponse
from modules.auth.schemas.register_request_schema import RegisterRequest

from motor.motor_asyncio import AsyncIOMotorDatabase
from core.db.motor import database

from modules.users.adapters.mongo_user_repository import MongoUserRepository
from modules.companies.adopters.mongo_company_repository import MongoCompanyRepository

from modules.auth.services.register import RegisterService

from modules.auth.schemas.login_response_schema import LoginResponse
from modules.auth.schemas.login_request_schema import LoginRequest

from modules.auth.services.login import LoginService

from modules.auth.adapters.mongo_token_blacklist_repository import MongoTokenBlacklistRepository



from modules.auth.services.logout import LogoutService
router =APIRouter(
    prefix="/auth",
    tags=["auth"]
)

_bearer =HTTPBearer()

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(database.get_database)
) -> RegisterResponse:
    
    user_repository = MongoUserRepository(db)
    company_repository =MongoCompanyRepository(db)
    
    service = RegisterService(
        user_reader= user_repository,
        user_writer= user_repository,
        company_writer= company_repository
    )
    
    return await service.execute(data)

@router.post(
    "/login",
    response_model= LoginResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    data:LoginRequest, 
    db: AsyncIOMotorDatabase =Depends(database.get_database)
    ) -> LoginResponse :
    user_repository =MongoUserRepository(db)
    
    service = LoginService(
        user_reader=user_repository
    )
    
    return await service.execute(data)

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncIOMotorDatabase = Depends(database.get_database),
):
    token_blacklist_repository = MongoTokenBlacklistRepository(db)
     
    service = LogoutService(
        blacklisted_token_write=token_blacklist_repository,
        blacklisted_token_read=token_blacklist_repository
    )
    
    await service.execute(credentials.credentials)