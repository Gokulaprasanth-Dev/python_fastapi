from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from modules.companies.model import CompanyModel


class MongoCompanyRepository:
    collection = "companies"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.col = db[self.collection]

    async def create_company(
        self,
        company: CompanyModel,
        session: AsyncIOMotorClientSession | None = None,
    ) -> str:
        """Fix 16: accept optional session so callers inside a UoW can enroll this write."""
        company_dict = company.model_dump(mode="json")
        result = await self.col.insert_one(company_dict, session=session)
        return str(result.inserted_id)
