from uuid import UUID

from core.events.event_bus import EventBus, NoOpEventBus
from core.events.schemas import UserUpdatedEvent
from modules.users.protocols import UserReader, UserWriter
from modules.users.schemas.update_user_request_schema import UpdateUserRequest
from modules.users.schemas.update_user_response_schema import UpdateUserResponse
from modules.users.exceptions import UserNotFoundError


class UpdateUserService:
    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        event_bus: EventBus | None = None,
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        # Default to no-op so callers that haven't wired the bus yet still work.
        self.event_bus: EventBus = event_bus or NoOpEventBus()

    async def execute(self, user_id: str, data: UpdateUserRequest) -> UpdateUserResponse:
        user = await self.user_reader.get_user_by_id(user_id)

        if not user:
            raise UserNotFoundError(user_id)

        updates = data.model_dump(exclude_none=True)

        # PhoneNumber serialises to an E.164 string — keep it as-is.
        if "phone" in updates:
            updates["phone"] = str(updates["phone"])

        await self.user_writer.update_user(user_id, updates)

        # Publish a typed event so downstream consumers can react to profile changes.
        event = UserUpdatedEvent(
            user_id=user_id,
            updated_fields=list(updates.keys()),
        )
        await self.event_bus.publish(event.event_type, event.model_dump())

        # Merge updates into current user doc for response.
        merged = {**user, **updates}

        return UpdateUserResponse(
            user_id=merged["id"],
            full_name=merged.get("full_name"),
            phone=merged.get("phone"),
            gender=merged.get("gender"),
            desc=merged.get("desc"),
            profile_image_url=merged.get("profile_image_url"),
        )
