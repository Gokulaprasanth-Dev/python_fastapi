from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.users.model import UserModel

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