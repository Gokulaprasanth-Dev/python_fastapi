from typing import Protocol

from modules.companies.models import CompanyDocument


class CompanyWriter(Protocol):
    async def insert(self, company: CompanyDocument) -> None: ...
