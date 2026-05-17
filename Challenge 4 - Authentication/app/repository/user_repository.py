from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import database
from app.models.users_model import UserModel

class UserRepository:
    
    def __init__(self):
        db = database.get_database()
        self.collection= db["users"]

    async def create_user(self,user: UserModel):
        user_dict= user.model_dump()
        
        result= await self.collection.insert_one(
            user_dict
        )
        
        return str(result.inserted_id)
    
    async def get_user_by_email(self,email: str) -> dict:
        return await self.collection.find_one({
            "email" :email
        })
    
    async def get_user_by_id(self, user_id: str) ->dict:
        return await self.collection.find_one({
           "_id" : ObjectId(user_id)
        })        
        
    async def update_profile(self, user_id: str, update_data :dict):
        
        update_data["updated_at"]= datetime.now(timezone.utc)
        
        await self.collection.update_one(
            {
                "_id":ObjectId(user_id)
            },
            {
                "$set": update_data
            }
            )
        
    async def update_profile_image(self,user_id:str,image_url:str):
        
        await self.collection.update_one(
            {
                "_id": ObjectId(user_id)
            },
            {
                "$set":{
                    "profile_image": image_url,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
    async def update_last_login(self, user_id: str):
        await self.collection.update_one(
            {
                "_id": ObjectId(user_id)
            },
            {
                "$set":{
                    "last_login": datetime.now(timezone.utc)
                }
            }
        )