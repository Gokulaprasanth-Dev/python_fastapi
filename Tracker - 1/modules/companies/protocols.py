from typing import Protocol

from motor.motor_asyncio import AsyncIOMotorClientSession

from modules.companies.model import CompanyModel


class CompanyWriter(Protocol):
    async def create_company(
        self,
        company: CompanyModel,
        session: AsyncIOMotorClientSession | None = None,
    ) -> str: ...


class CompanyReader(Protocol):
    """
    Read-side protocol for the companies module.

    Stub methods are declared here so the protocol seam exists before the
    implementations are needed. Each method raises NotImplementedError
    rather than being a bare ellipsis so any accidental call is loud.
    """
    async def get_company_by_id(self, company_id: str) -> dict | None: ...
