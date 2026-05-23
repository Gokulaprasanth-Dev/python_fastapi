from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.db.motor import database
from modules.users.adapters.mongo_user_repository import MongoUserRepository
from modules.users.schemas.update_user_request_schema import UpdateUserRequest
from modules.users.schemas.update_user_response_schema import UpdateUserResponse
from modules.users.services.update_user import UpdateUserService
from modules.users.services.delete_user import SoftDeleteUserService, HardDeleteUserService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch(
    "/{user_id}",
    response_model=UpdateUserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
) -> UpdateUserResponse:
    repo = MongoUserRepository(db)
    service = UpdateUserService(user_reader=repo, user_writer=repo)
    return await service.execute(user_id, data)


@router.delete(
    "/{user_id}/soft",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def soft_delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
):
    repo = MongoUserRepository(db)
    service = SoftDeleteUserService(user_reader=repo, user_writer=repo)
    await service.execute(user_id)


@router.delete(
    "/{user_id}/hard",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def hard_delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(database.get_database),
):
    repo = MongoUserRepository(db)
    service = HardDeleteUserService(user_reader=repo, user_writer=repo)
    await service.execute(user_id)