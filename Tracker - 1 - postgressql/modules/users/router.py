from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.postgres import get_db_session
from core.dependencies.auth import CurrentUser, require_role
from core.exceptions.base import ForbiddenError
from core.storage.dependencies import Storage

from modules.users.adapters.postgres_user_repository import PostgresUserRepository
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
    session: AsyncSession = Depends(get_db_session),
) -> UpdateUserResponse:
    if current_user["sub"] != user_id:
        raise ForbiddenError("You can only update your own profile")
    repo = PostgresUserRepository(session)
    service = UpdateUserService(user_reader=repo, user_writer=repo)
    return await service.execute(user_id, data)


@router.delete(
    "/{user_id}/soft",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def soft_delete_user(
    user_id: str,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
):
    if current_user["sub"] != user_id and current_user.get("role") != "admin":
        raise ForbiddenError("You can only delete your own account")
    repo = PostgresUserRepository(session)
    service = SoftDeleteUserService(user_reader=repo, user_writer=repo)
    await service.execute(user_id)


@router.delete(
    "/{user_id}/hard",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def hard_delete_user(
    user_id: str,
    storage: Storage,
    session: AsyncSession = Depends(get_db_session),
):
    repo = PostgresUserRepository(session)
    # Purge blacklisted tokens via direct session query
    from sqlalchemy import delete
    from core.db.tables.token_blacklist_table import TokenBlacklistTable
    
    async def _purge_tokens(user_id: str):
        await session.execute(
            delete(TokenBlacklistTable).where(TokenBlacklistTable.user_id == user_id)
        )

    service = HardDeleteUserService(
        user_reader=repo,
        user_writer=repo,
        storage=storage,
        blacklist_col=type("_Col", (), {
            "delete_many": lambda self, q: _purge_tokens(q.get("user_id", ""))
        })(),
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
    current_user: CurrentUser = Depends(),
    storage: Storage = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> AvatarUploadResponse:
    if current_user["sub"] != user_id:
        raise ForbiddenError("You can only update your own avatar")
    repo = PostgresUserRepository(session)
    service = AvatarUploadService(
        user_reader=repo,
        user_writer=repo,
        storage=storage,
    )
    return await service.execute(user_id, file)
