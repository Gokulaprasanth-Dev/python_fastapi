from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from modules.users.model import UserModel
from modules.users.schemas.update_user_request_schema import UpdateUserRequest

from datetime import datetime, timezone


def _map_user(doc: dict | None) -> dict | None:
    """
    Map a raw MongoDB document to a clean user dict.

    - Strips the internal _id (ObjectId) field.
    - Guarantees the 'id' key is always present as a string.

    Fix 14: callers no longer need to worry about _id leaking through
    or KeyError on 'id' if the document shape is unexpected.
    """
    if doc is None:
        return None
    doc.pop("_id", None)
    # Ensure id is always a plain string regardless of how it was stored
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
        """Fix 16: accept optional session so callers inside a UoW can enroll this write."""
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
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
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
            {"$set": {
                "profile_image_url": url,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }},
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
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }},
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
