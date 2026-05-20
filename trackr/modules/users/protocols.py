from typing import Protocol

from modules.users.models import UserDocument


class UserReader(Protocol):
    async def email_exists(self, email: str) -> bool: ...
    async def get_by_email(self, email: str) -> UserDocument | None: ...


class UserWriter(Protocol):
    async def insert(self, user: UserDocument) -> None: ...
