from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.users.protocols import UserReader, UserWriter
from modules.users.exceptions import UserNotFoundError


class SoftDeleteUserService:
    def __init__(self, user_reader: UserReader, user_writer: UserWriter) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer

    async def execute(self, user_id: str) -> None:
        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        await self.user_writer.soft_delete_user(user_id)


class HardDeleteUserService:
    """
    Permanently removes a user and their associated data:
      1. Avatar file deleted from S3 (if one exists).
      2. Blacklisted tokens for the user purged from the collection.
      3. User document hard-deleted from MongoDB.

    The storage and blacklist dependencies are optional so callers that
    don't have them wired can still use the service in contexts where
    cascades are handled externally (e.g. integration tests).
    """

    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        storage=None,
        blacklist_col=None,
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        self._storage = storage
        self._blacklist_col = blacklist_col

    async def execute(self, user_id: str) -> None:
        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # 1. Delete avatar from S3 if present
        avatar_url: str | None = user.get("profile_image_url")
        if avatar_url and self._storage is not None:
            try:
                from modules.users.services.upload_avatar import AvatarUploadService
                key = AvatarUploadService._extract_key_static(avatar_url)
                await self._storage.delete_file(key)
            except Exception:
                # Non-fatal — log and continue so the user record is still removed
                import logging
                logging.getLogger(__name__).warning(
                    "Failed to delete avatar during hard-delete for user %s", user_id
                )

        # 2. Purge blacklisted tokens belonging to this user
        if self._blacklist_col is not None:
            await self._blacklist_col.delete_many({"user_id": user_id})

        # 3. Remove the user document
        await self.user_writer.hard_delete_user(user_id)
