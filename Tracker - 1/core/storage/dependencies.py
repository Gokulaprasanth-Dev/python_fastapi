from typing import Annotated

from fastapi import Depends

from core.storage.client import S3StorageClient
from core.storage.protocol import StorageProtocol


def get_storage() -> StorageProtocol:
    return S3StorageClient()


Storage = Annotated[StorageProtocol, Depends(get_storage)]