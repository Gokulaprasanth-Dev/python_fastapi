import logging

from core.events.event_bus import EventBus, NoOpEventBus
from core.events.schemas import UserDeletedEvent
from modules.users.protocols import UserReader, UserWriter
from modules.users.exceptions import UserNotFoundError
from shared.utils.storage_keys import extract_avatar_key

logger = logging.getLogger(__name__)


class SoftDeleteUserService:
    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        event_bus: EventBus | None = None,
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.event_bus: EventBus = event_bus or NoOpEventBus()

    async def execute(self, user_id: str) -> None:
        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        await self.user_writer.soft_delete_user(user_id)

        event = UserDeletedEvent(user_id=user_id, hard_delete=False)
        await self.event_bus.publish(event.event_type, event.model_dump())


class HardDeleteUserService:
    """
    Permanently removes a user and their associated data:
      1. Avatar file deleted from S3 (if one exists).
      2. Blacklisted tokens for the user purged from the collection.
      3. User document hard-deleted from MongoDB.
      4. UserDeletedEvent published to the event bus.
    """

    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        storage=None,
        blacklist_col=None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        self._storage = storage
        self._blacklist_col = blacklist_col
        self.event_bus: EventBus = event_bus or NoOpEventBus()

    async def execute(self, user_id: str) -> None:
        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # 1. Delete avatar from S3 if present.
        avatar_url: str | None = user.get("profile_image_url")
        if avatar_url and self._storage is not None:
            try:
                key = extract_avatar_key(avatar_url)
                await self._storage.delete_file(key)
            except Exception:
                logger.warning(
                    "Failed to delete avatar during hard-delete for user %s",
                    user_id,
                )

        # 2. Purge blacklisted tokens belonging to this user.
        if self._blacklist_col is not None:
            await self._blacklist_col.delete_many({"user_id": user_id})

        # 3. Remove the user document.
        await self.user_writer.hard_delete_user(user_id)

        # 4. Publish deletion event.
        event = UserDeletedEvent(user_id=user_id, hard_delete=True)
        await self.event_bus.publish(event.event_type, event.model_dump())
