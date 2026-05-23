from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.users.model import UserModel
from modules.users.schemas.update_user_request_schema import UpdateUserRequest

from datetime import datetime, timezone


class MongoUserRepository:
    collection = "users"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.col = db[self.collection]

    async def email_exist(self, email: str) -> bool:
        result = await self.col.find_one({"email": email}, {"id": 1})
        return result is not None

    async def create_user(self, user: UserModel) -> str:
        user_dict = user.model_dump(mode="json")
        result = await self.col.insert_one(user_dict)
        return str(result.inserted_id)

    async def get_user_by_email(self, email: str) -> dict | None:
        return await self.col.find_one({"email": email})

    async def get_user_by_id(self, user_id: str) -> dict | None:
        return await self.col.find_one({"id": user_id})

    async def update_user(self, user_id: str, updates: dict) -> bool:
        """
        FIX #9: Internal method used by services that pass pre-validated
        UpdateUserRequest data. The service layer calls
        data.model_dump(exclude_none=True) before calling this method,
        so the dict is already sanitised to only allowed fields.
        """
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": updates},
        )
        return result.matched_count > 0

    async def update_profile_image(self, user_id: str, url: str) -> bool:
        """
        FIX #9: Dedicated method for avatar updates so the avatar service
        does not need to pass a raw dict with arbitrary keys.
        """
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": {
                "profile_image_url": url,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }},
        )
        return result.matched_count > 0

    async def soft_delete_user(self, user_id: str) -> bool:
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }},
        )
        return result.matched_count > 0

    async def hard_delete_user(self, user_id: str) -> bool:
        result = await self.col.delete_one({"id": user_id})
        return result.deleted_count > 0