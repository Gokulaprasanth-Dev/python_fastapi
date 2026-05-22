from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.auth.models.blacklisted_token_model import BlacklistedTokenModel

class MongoTokenBlacklistRepository():
    collection ="token_blacklist"
    
    def __init__(
        self,
        db:AsyncIOMotorDatabase
        )-> None:
        self.col = db[self.collection]
        
    async def is_token_blacklisted(self,jti: str) -> bool:
        result = await self.col.find_one({"jti": jti})
        return result is not None    
    
    async def create_blacklisted_token(self,data: BlacklistedTokenModel):
        token_blacklist_dict =data.model_dump(mode="json")
        
        result =await self.col.insert_one(
            token_blacklist_dict
        )
        
        return str(result.inserted_id)