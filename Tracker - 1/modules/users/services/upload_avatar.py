from uuid import uuid4

from fastapi import UploadFile

from core.storage.protocol import StorageProtocol
from modules.users.exceptions import UserNotFoundError, UnsupportedFileTypeError, FileTooLargeError
from modules.users.protocols import UserReader, UserWriter
from modules.users.schemas.avatar_upload_response_schema import AvatarUploadResponse


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

EXTENSION_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

# 5 MB hard limit — increase via config if needed
MAX_AVATAR_BYTES = 5 * 1024 * 1024


class AvatarUploadService:
    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        storage: StorageProtocol,
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.storage = storage

    async def execute(self, user_id: str, file: UploadFile) -> AvatarUploadResponse:
        # Fix 4: validate content-type before touching the user record
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedFileTypeError(
                content_type=file.content_type or "unknown",
                allowed=sorted(ALLOWED_CONTENT_TYPES),
            )

        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Fix 4: enforce file size limit — read into memory once, check, then use
        file_bytes = await file.read()
        if len(file_bytes) > MAX_AVATAR_BYTES:
            raise FileTooLargeError(max_bytes=MAX_AVATAR_BYTES)

        old_url: str | None = user.get("profile_image_url")
        if old_url:
            old_key = self._extract_key(old_url)
            await self.storage.delete_file(old_key)

        ext = EXTENSION_MAP.get(file.content_type, "jpg")
        key = f"avatars/{user_id}/{uuid4()}.{ext}"

        new_url = await self.storage.upload_file(
            file_bytes=file_bytes,
            key=key,
            content_type=file.content_type,
        )

        await self.user_writer.update_profile_image(user_id, new_url)

        return AvatarUploadResponse(
            user_id=user["id"],
            profile_image_url=new_url,
        )

    def _extract_key(self, url: str) -> str:
        parts = url.split("/")
        avatar_index = next(
            (i for i, p in enumerate(parts) if p == "avatars"), None
        )
        if avatar_index is None:
            return url
        return "/".join(parts[avatar_index:])
