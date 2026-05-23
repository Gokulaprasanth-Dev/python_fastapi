from typing import Protocol

from motor.motor_asyncio import AsyncIOMotorClientSession

from modules.users.model import UserModel


class UserReader(Protocol):
    async def email_exist(self, email: str) -> bool: ...
    async def get_user_by_email(self, email: str) -> dict | None: ...
    async def get_user_by_id(self, user_id: str) -> dict | None: ...


class UserWriter(Protocol):
    async def create_user(
        self,
        data: UserModel,
        session: AsyncIOMotorClientSession | None = None,
    ) -> str: ...

    async def update_user(
        self,
        user_id: str,
        updates: dict,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool: ...

    async def update_profile_image(
        self,
        user_id: str,
        url: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool: ...

    async def soft_delete_user(
        self,
        user_id: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool: ...

    async def hard_delete_user(
        self,
        user_id: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool: ...
