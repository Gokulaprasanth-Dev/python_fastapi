"""Unit tests for HardDeleteUserService — cascade delete logic."""

import pytest
from unittest.mock import AsyncMock

from modules.users.services.delete_user import HardDeleteUserService, SoftDeleteUserService
from modules.users.exceptions import UserNotFoundError
from tests.conftest import FakeUserRepository, FakeStorage


@pytest.mark.asyncio
async def test_hard_delete_removes_user(existing_user, user_repo, storage):
    user_id = existing_user["id"]
    service = HardDeleteUserService(
        user_reader=user_repo,
        user_writer=user_repo,
        storage=storage,
    )
    await service.execute(user_id)
    assert await user_repo.get_user_by_id(user_id) is None


@pytest.mark.asyncio
async def test_hard_delete_removes_avatar_from_s3(user_repo, storage):
    from modules.users.model import UserModel
    from uuid import uuid4

    user = UserModel(
        company_id=uuid4(),
        email="carol@example.com",
        hashed_password="x",
        full_name="Carol",
        profile_image_url="https://bucket.s3.amazonaws.com/avatars/carol-id/photo.jpg",
    )
    user_repo._seed(user)
    user_id = str(user.id)

    service = HardDeleteUserService(
        user_reader=user_repo,
        user_writer=user_repo,
        storage=storage,
    )
    await service.execute(user_id)

    assert "avatars/carol-id/photo.jpg" in storage.deleted


@pytest.mark.asyncio
async def test_hard_delete_purges_blacklist_tokens(existing_user, user_repo):
    user_id = existing_user["id"]

    # Use a real async mock for the collection.
    blacklist_col = AsyncMock()
    blacklist_col.delete_many = AsyncMock()

    service = HardDeleteUserService(
        user_reader=user_repo,
        user_writer=user_repo,
        blacklist_col=blacklist_col,
    )
    await service.execute(user_id)

    blacklist_col.delete_many.assert_called_once_with({"user_id": user_id})


@pytest.mark.asyncio
async def test_hard_delete_nonexistent_user_raises(user_repo):
    service = HardDeleteUserService(user_reader=user_repo, user_writer=user_repo)

    with pytest.raises(UserNotFoundError):
        await service.execute("nonexistent-id")


@pytest.mark.asyncio
async def test_hard_delete_continues_when_avatar_delete_fails(existing_user, user_repo):
    """S3 failure during avatar deletion must not prevent user record removal."""
    user_id = existing_user["id"]
    user_repo._store[user_id]["profile_image_url"] = (
        "https://bucket.s3.amazonaws.com/avatars/x/photo.jpg"
    )

    broken_storage = AsyncMock()
    broken_storage.delete_file = AsyncMock(side_effect=RuntimeError("S3 unavailable"))

    service = HardDeleteUserService(
        user_reader=user_repo,
        user_writer=user_repo,
        storage=broken_storage,
    )
    # Should not raise — logs the warning and continues.
    await service.execute(user_id)
    assert await user_repo.get_user_by_id(user_id) is None


@pytest.mark.asyncio
async def test_soft_delete_sets_is_active_false(existing_user, user_repo):
    user_id = existing_user["id"]
    service = SoftDeleteUserService(user_reader=user_repo, user_writer=user_repo)
    await service.execute(user_id)

    doc = await user_repo.get_user_by_id(user_id)
    assert doc["is_active"] is False
