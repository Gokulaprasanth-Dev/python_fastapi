from typing import Protocol

from modules.companies.model import CompanyModel

# class UserReader(Protocol):
#     async def email_exist(self,email:str) ->True: ...
    
class CompanyWriter(Protocol):
    async def create_company(self,company:CompanyModel): ...