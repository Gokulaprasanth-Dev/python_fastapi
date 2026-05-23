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
    def __init__(self, user_reader: UserReader, user_writer: UserWriter) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer

    async def execute(self, user_id: str) -> None:
        user = await self.user_reader.get_user_by_id(user_id)

        if not user:
            raise UserNotFoundError(user_id)

        await self.user_writer.hard_delete_user(user_id)