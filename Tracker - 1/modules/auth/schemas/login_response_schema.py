from uuid import UUID

from shared.schemas.base_schema import BaseSchema

class LoginResponse(BaseSchema):
    access_token: str
    token_type: str
    user_id: UUID
    company_id: UUID
    full_name: str
    email: str