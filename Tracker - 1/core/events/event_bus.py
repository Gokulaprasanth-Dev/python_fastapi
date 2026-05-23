from typing import Any, Protocol


class EventBus(Protocol):
    """
    Abstract event bus.

    Services publish domain events here.
    Today it's a no-op. Later, swap NoOpEventBus for a
    KafkaEventBus or RabbitMQEventBus without touching service code.

    Usage:
        await event_bus.publish("user.logged_out", {"user_id": "..."})
    """

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None: ...


class NoOpEventBus:
    """
    In-process no-op event bus for development and early production.

    Drop-in replacement once a real message broker is available.
    """

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        pass