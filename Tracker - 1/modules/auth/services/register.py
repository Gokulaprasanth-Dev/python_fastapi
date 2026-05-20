from modules.users.protocols import UserReader,UserWriter
from modules.companies.protocols import CompanyWriter

from modules.auth.schemas.register_request_schema import RegisterRequest
from modules.auth.schemas.register_response_schema import RegisterResponse

from modules.auth.exceptions import EmailAlreadyExistsError

from modules.companies.model import CompanyModel
from modules.users.model import UserModel

from core.security.password import hash_password
class RegisterService:
    def __init__(
        self,
        user_reader: UserReader,
        user_writer: UserWriter,
        company_writer: CompanyWriter
    ) -> None:
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.company_writer = company_writer
        
    async def execute(self, data : RegisterRequest) -> RegisterResponse:
        
        if await self.user_reader.email_exist(data.email):
            raise EmailAlreadyExistsError(data.email)
        
        company =CompanyModel(
            name = data.company_name,
            country = data.company_country,            
            industry =data.company_industry
        )
        
        user = UserModel(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            phone=data.phone,
            company_id=company.id,
        )
        
        await self.user_writer.create_user(user)
        await self.company_writer.create_company(company)
        
        return RegisterResponse(
                user_id= user.id,
                company_id= company.id,
                email= user.email,
                full_name= user.full_name,
                company_name= company.name
        )
        