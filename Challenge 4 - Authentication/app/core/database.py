from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    
    client: AsyncIOMotorClient | None =None

    async def connect(self):
        self.client=AsyncIOMotorClient(
            settings.mongodb_url
        )
        print("Mongodb connected successfully")
      
    async def disconnect(self):
        
        if self.client:
            self.client.close()
        print("Mongodb connection closed")          
        
    def get_database(self):
        if self.client is None:
            raise RuntimeError(
                "Database not connected. Ensure the lifespan event has triggered database.connect()."
            )
        return self.client[settings.database_name]
    
database = Database()    