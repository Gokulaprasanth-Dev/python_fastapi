from uuid import uuid4

from fastapi import UploadFile

from core.storage.protocol import StorageProtocol
from modules.users.exceptions import (
    UserNotFoundError,
    UnsupportedFileTypeError,
    FileTooLargeError,
    InvalidImageContentError,
)
from modules.users.protocols import UserReader, UserWriter
from modules.users.schemas.avatar_upload_response_schema import AvatarUploadResponse
from shared.utils.image_validation import validate_image_magic_bytes
from shared.utils.storage_keys import extract_avatar_key


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
        # 1. Validate declared Content-Type before reading any bytes.
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedFileTypeError(
                content_type=file.content_type or "unknown",
                allowed=sorted(ALLOWED_CONTENT_TYPES),
            )

        user = await self.user_reader.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # 2. Read into memory once, enforce size limit.
        file_bytes = await file.read()
        if len(file_bytes) > MAX_AVATAR_BYTES:
            raise FileTooLargeError(max_bytes=MAX_AVATAR_BYTES)

        # 3. Validate actual file bytes against known magic bytes.
        #    Content-Type headers are client-controlled; this closes the gap
        #    where a malicious client sets Content-Type: image/jpeg on a
        #    non-image payload (e.g. a script or executable).
        if not validate_image_magic_bytes(file_bytes, file.content_type):
            raise InvalidImageContentError(content_type=file.content_type)

        old_url: str | None = user.get("profile_image_url")
        if old_url:
            await self.storage.delete_file(extract_avatar_key(old_url))

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
