from fastapi import APIRouter, Depends, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.db.motor import database
from core.dependencies.auth import CurrentUser, require_role
from core.exceptions.base import ForbiddenError
from core.storage.dependencies import Storage

from modules.auth.adapters.mongo_token_blacklist_repository import MongoTokenBlacklistRepository
from modules.users.adapters.mongo_user_repository import MongoUserRepository
from modules.users.schemas.update_user_request_schema import UpdateUserRequest
from modules.users.schemas.update_user_response_schema import UpdateUserResponse
from modules.users.schemas.avatar_upload_response_schema import AvatarUploadResponse
from modules.users.services.update_user import UpdateUserService
from modules.users.services.delete_user import SoftDeleteUserService, HardDeleteUserService
from modules.users.services.upload_avatar import AvatarUploadService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch(
    "/{user_id}",
    response_model=UpdateUserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
) -> UpdateUserResponse:
    if current_user["sub"] != user_id:
        raise ForbiddenError("You can only update your own profile")
    repo = MongoUserRepository(db)
    service = UpdateUserService(user_reader=repo, user_writer=repo)
    return await service.execute(user_id, data)


@router.delete(
    "/{user_id}/soft",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def soft_delete_user(
    user_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
):
    if current_user["sub"] != user_id and current_user.get("role") != "admin":
        raise ForbiddenError("You can only delete your own account")
    repo = MongoUserRepository(db)
    service = SoftDeleteUserService(user_reader=repo, user_writer=repo)
    await service.execute(user_id)


@router.delete(
    "/{user_id}/hard",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def hard_delete_user(
    user_id: str,
    storage: Storage = ...,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
):
    repo = MongoUserRepository(db)
    blacklist_col = db["token_blacklist"]
    service = HardDeleteUserService(
        user_reader=repo,
        user_writer=repo,
        storage=storage,
        blacklist_col=blacklist_col,
    )
    await service.execute(user_id)


@router.post(
    "/{user_id}/avatar",
    response_model=AvatarUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_avatar(
    user_id: str,
    file: UploadFile = File(...),
    current_user: CurrentUser = ...,
    storage: Storage = ...,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
) -> AvatarUploadResponse:
    if current_user["sub"] != user_id:
        raise ForbiddenError("You can only update your own avatar")
    repo = MongoUserRepository(db)
    service = AvatarUploadService(
        user_reader=repo,
        user_writer=repo,
        storage=storage,
    )
    return await service.execute(user_id, file)
