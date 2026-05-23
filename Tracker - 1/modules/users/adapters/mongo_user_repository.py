from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.users.model import UserModel

from datetime import datetime, timezone

class MongoUserRepository():
    collection = "users"
    
    def __init__(self,db:AsyncIOMotorDatabase )-> None:
        self.col =db[self.collection]
        
    async def email_exist(self,email:str) ->True:
        result = await self.col.find_one(
            {
                "email": email
            },
            {
                "id":1
            }
        )
        return result is not None
    
    async def create_user(self,user: UserModel):
        user_dict= user.model_dump(mode="json")
        
        result= await self.col.insert_one(
            user_dict
        )
        
        return str(result.inserted_id)
    
    async def get_user_by_email(self,email:str) -> dict:
        return await self.col.find_one(
            {
                "email":email
            }
        )
        
    async def get_user_by_id(self, user_id: str) -> dict | None:
        return await self.col.find_one({"id": user_id})

    async def update_user(self, user_id: str, updates: dict) -> bool:
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": updates},
        )
        return result.matched_count > 0

    async def soft_delete_user(self, user_id: str) -> bool:
        result = await self.col.update_one(
            {"id": user_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc)
            }},
        )
        return result.matched_count > 0

    async def hard_delete_user(self, user_id: str) -> bool:
        result = await self.col.delete_one({"id": user_id})
        return result.deleted_count > 0
