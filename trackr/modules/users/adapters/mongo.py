from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.users.models import UserDocument


class MongoUserAdapter:
    COLLECTION = "users"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]

    async def email_exists(self, email: str) -> bool:
        doc = await self._col.find_one({"email": email}, {"_id": 1})
        return doc is not None

    async def get_by_email(self, email: str) -> UserDocument | None:
        doc = await self._col.find_one({"email": email})
        if doc is None:
            return None
        return UserDocument(
            id=UUID(doc["_id"]),
            full_name=doc["full_name"],
            email=doc["email"],
            hashed_password=doc["hashed_password"],
            phone=doc["phone"],
            company_id=UUID(doc["company_id"]),
            role=doc["role"],
            is_active=doc["is_active"],
            created_at=doc["created_at"],
        )

    async def insert(self, user: UserDocument) -> None:
        await self._col.insert_one(
            {
                "_id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "hashed_password": user.hashed_password,
                "phone": user.phone,
                "company_id": str(user.company_id),
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
            }
        )
