from typing import Callable, Awaitable

from modules.users.protocols import UserReader, UserWriter
from modules.companies.protocols import CompanyWriter

from modules.auth.schemas.register_request_schema import RegisterRequest
from modules.auth.schemas.register_response_schema import RegisterResponse

from modules.auth.exceptions import EmailAlreadyExistsError

from modules.companies.model import CompanyModel
from modules.users.model import UserModel

from core.security.password import hash_password
from core.uow.mongo_unit_of_work import UnitOfWork


class RegisterService:
    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        company_writer: CompanyWriter,
        uow: UnitOfWork,
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.company_writer = company_writer
        self.uow = uow

    async def execute(self, data: RegisterRequest) -> RegisterResponse:

        if await self.user_reader.email_exist(data.email):
            raise EmailAlreadyExistsError(data.email)

        company = CompanyModel(
            name=data.company_name,
            country=data.company_country,
            industry=data.company_industry,
        )

        user = UserModel(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            phone=str(data.phone) if data.phone else None,
            company_id=company.id,
        )

        # Fix 16: pass uow.session to both writes so MongoDB actually enrolls
        # them in the same transaction. Without this, the UoW starts a session
        # but the insert_one calls run outside it.
        async with self.uow:
            await self.company_writer.create_company(company, session=self.uow.session)
            await self.user_writer.create_user(user, session=self.uow.session)

        return RegisterResponse(
            user_id=user.id,
            company_id=company.id,
            email=user.email,
            full_name=user.full_name,
            company_name=company.name,
        )
