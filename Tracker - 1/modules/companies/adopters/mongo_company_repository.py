from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.companies.model import CompanyModel

class MongoCompanyRepository():
    collection = "companies"
    
    def __init__(self,db:AsyncIOMotorDatabase )-> None:
        self.col =db[self.collection]
        
    async def create_company(self,company: CompanyModel):
        company_dict= company.model_dump(mode="json")
        
        result= await self.col.insert_one(
            company_dict
        )
        
        return str(result.inserted_id)