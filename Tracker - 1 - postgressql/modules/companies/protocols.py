from typing import Protocol

from modules.companies.model import CompanyModel


class CompanyWriter(Protocol):
    async def create_company(self, company: CompanyModel, session=None) -> str: ...


class CompanyReader(Protocol):
    async def get_company_by_id(self, company_id: str) -> dict | None: ...
