from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.tables.company_table import CompanyTable
from modules.companies.model import CompanyModel


class PostgresCompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_company(self, company: CompanyModel, session: AsyncSession | None = None) -> str:
        db = session or self.session
        row = CompanyTable(
            id=company.id,
            name=company.name,
            country=company.country,
            industry=company.industry,
            is_active=company.is_active,
            is_verified=company.is_verified,
        )
        db.add(row)
        await db.flush()
        return str(company.id)

    async def get_company_by_id(self, company_id: str) -> dict | None:
        import uuid
        try:
            cid = uuid.UUID(company_id)
        except ValueError:
            return None
        result = await self.session.execute(
            select(CompanyTable).where(CompanyTable.id == cid)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {
            "id": str(row.id),
            "name": row.name,
            "country": row.country,
            "industry": row.industry,
            "is_active": row.is_active,
            "is_verified": row.is_verified,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
