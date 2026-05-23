from typing import Protocol


class StorageProtocol(Protocol):
    async def upload_file(
        self,
        file_bytes: bytes,
        key: str,
        content_type: str,
    ) -> str:
        """Upload a file and return its public URL."""
        ...

    async def delete_file(self, key: str) -> None:
        """Delete a file by its storage key."""
        ...