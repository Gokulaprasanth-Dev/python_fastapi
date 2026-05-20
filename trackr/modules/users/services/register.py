from modules.companies.models import CompanyDocument
from modules.companies.protocols import CompanyWriter
from modules.users.exceptions import EmailAlreadyExistsError
from modules.users.models import UserDocument
from modules.users.protocols import UserReader, UserWriter
from modules.users.schemas.requests import RegisterRequest
from modules.users.schemas.responses import RegisterResponse
from core.security.password import hash_password


class RegisterService:
    """
    Orchestrates company + admin user creation atomically.

    Depends only on protocols — no FastAPI, no Motor, no HTTP concepts.
    Can be called from a router, a CLI, a Celery task, or a test.

    NOTE (OQ-1): Two inserts are sequential without a Motor ClientSession
    transaction. A replica set or Atlas is required for multi-document
    transactions. Wire a ClientSession here once the environment supports it.
    """

    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        company_writer: CompanyWriter,
    ) -> None:
        self._user_reader = user_reader
        self._user_writer = user_writer
        self._company_writer = company_writer

    async def execute(self, data: RegisterRequest) -> RegisterResponse:
        # 1. Guard — application-level email uniqueness check.
        #    Do NOT rely on the DB unique index alone: there is a race-condition
        #    window between the check and the insert. The index is a safety net,
        #    not the primary guard.
        if await self._user_reader.email_exists(data.email):
            raise EmailAlreadyExistsError(data.email)

        # 2. Build company document (pure Python — no DB yet)
        company = CompanyDocument(
            name=data.company_name,
            country=data.company_country,
            industry=data.company_industry,
        )

        # 3. Build user document (pure Python — no DB yet)
        user = UserDocument(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            phone=data.phone,
            company_id=company.id,
        )

        # 4. Persist — company first so the foreign key exists if we add
        #    referential checks later.
        await self._company_writer.insert(company)
        await self._user_writer.insert(user)

        return RegisterResponse(
            user_id=user.id,
            company_id=company.id,
            email=user.email,
            full_name=user.full_name,
            company_name=company.name,
        )