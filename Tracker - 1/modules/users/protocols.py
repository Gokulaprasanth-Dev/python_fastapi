from typing import Protocol

from modules.users.model import UserModel


class UserReader(Protocol):
    async def email_exist(self, email: str) -> bool: ...           # FIX #5: was -> True
    async def get_user_by_email(self, email: str) -> dict | None: ...
    async def get_user_by_id(self, user_id: str) -> dict | None: ...  # FIX #5: added missing method


class UserWriter(Protocol):
    async def create_user(self, data: UserModel) -> str: ...
    async def update_user(self, user_id: str, updates: dict) -> bool: ...
    async def update_profile_image(self, user_id: str, url: str) -> bool: ...  # FIX #9: dedicated method
    async def soft_delete_user(self, user_id: str) -> bool: ...
    async def hard_delete_user(self, user_id: str) -> bool: ...