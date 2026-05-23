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

# 5 MB hard limit
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
        # Validate content-type before reading any bytes
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedFileTypeError(
                content_type=file.content_type or "unknown",
                allowed=sorted(ALLOWED_CONTENT_TYPES),
            )

        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Enforce size limit — read into memory once, check, then use
        file_bytes = await file.read()
        if len(file_bytes) > MAX_AVATAR_BYTES:
            raise FileTooLargeError(max_bytes=MAX_AVATAR_BYTES)

        old_url: str | None = user.get("profile_image_url")
        if old_url:
            old_key = self._extract_key_static(old_url)
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

    @staticmethod
    def _extract_key_static(url: str) -> str:
        """
        Extract the S3 object key from a full avatar URL.

        Walks from the first 'avatars/' path segment to the end. If the
        sentinel is absent (e.g. an externally-set URL), returns the
        original URL unchanged — the caller should handle or log the error.
        """
        parts = url.split("/")
        avatar_index = next(
            (i for i, p in enumerate(parts) if p == "avatars"), None
        )
        if avatar_index is None:
            return url
        return "/".join(parts[avatar_index:])

    # Instance alias for backwards compatibility
    def _extract_key(self, url: str) -> str:
        return self._extract_key_static(url)
