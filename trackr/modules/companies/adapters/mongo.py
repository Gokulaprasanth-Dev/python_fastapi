from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.companies.models import CompanyDocument


class MongoCompanyAdapter:
    COLLECTION = "companies"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]

    async def insert(self, company: CompanyDocument) -> None:
        await self._col.insert_one(
            {
                "_id": str(company.id),
                "name": company.name,
                "country": company.country,
                "industry": company.industry,
                "created_at": company.created_at,
            }
        )
