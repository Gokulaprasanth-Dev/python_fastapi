from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from modules.users.model import UserModel


def _now() -> datetime:
    """Return the current UTC datetime. Used for updated_at stamps."""
    return datetime.now(timezone.utc)


def _map_user(doc: dict | None) -> dict | None:
    """
    Map a raw MongoDB document to a clean user dict.

    - Strips the internal _id (ObjectId) field.
    - Guarantees the 'id' key is always present as a string.
    """
    if doc is None:
        return None
    doc.pop("_id", None)
    if "id" in doc:
        doc["id"] = str(doc["id"])
    return doc


class MongoUserRepository:
    collection = "users"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.col = db[self.collection]

    async def email_exist(self, email: str) -> bool:
        result = await self.col.find_one({"email": email}, {"id": 1})
        return result is not None

    async def create_user(
        self,
        user: UserModel,
        session: AsyncIOMotorClientSession | None = None,
    ) -> str:
        user_dict = user.model_dump(mode="json")
        result = await self.col.insert_one(user_dict, session=session)
        return str(result.inserted_id)

    async def get_user_by_email(self, email: str) -> dict | None:
        doc = await self.col.find_one({"email": email})
        return _map_user(doc)

    async def get_user_by_id(self, user_id: str) -> dict | None:
        doc = await self.col.find_one({"id": user_id})
        return _map_user(doc)

    async def update_user(
        self,
        user_id: str,
        updates: dict,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool:
        # Store as a native datetime so MongoDB range queries work correctly.
        updates["updated_at"] = _now()
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": updates},
            session=session,
        )
        return result.matched_count > 0

    async def update_profile_image(
        self,
        user_id: str,
        url: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool:
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": {"profile_image_url": url, "updated_at": _now()}},
            session=session,
        )
        return result.matched_count > 0

    async def soft_delete_user(
        self,
        user_id: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool:
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": {"is_active": False, "updated_at": _now()}},
            session=session,
        )
        return result.matched_count > 0

    async def hard_delete_user(
        self,
        user_id: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> bool:
        result = await self.col.delete_one({"id": user_id}, session=session)
        return result.deleted_count > 0
