"""
Domain event schemas.

These Pydantic models define the guaranteed payload shape for every event
published on the EventBus. Consumers depend on these contracts; changing a
field here is a breaking change and requires a version bump.

When the NoOpEventBus is replaced with a real broker (Kafka, RabbitMQ),
serialise events using .model_dump() and deserialise with .model_validate().
"""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class UserLoggedOutEvent(BaseEvent):
    """Published when a user successfully logs out."""
    event_type: str = "user.logged_out"
    user_id: str
    jti: str


class UserRegisteredEvent(BaseEvent):
    """Published when a new user + company are created."""
    event_type: str = "user.registered"
    user_id: str
    company_id: str
    email: str


class UserUpdatedEvent(BaseEvent):
    """Published when a user's profile fields are changed."""
    event_type: str = "user.updated"
    user_id: str
    updated_fields: list[str]


class UserDeletedEvent(BaseEvent):
    """Published when a user is soft- or hard-deleted."""
    event_type: str = "user.deleted"
    user_id: str
    hard_delete: bool = False


class AvatarUploadedEvent(BaseEvent):
    """Published when a user's avatar is updated."""
    event_type: str = "user.avatar_uploaded"
    user_id: str
    profile_image_url: str
