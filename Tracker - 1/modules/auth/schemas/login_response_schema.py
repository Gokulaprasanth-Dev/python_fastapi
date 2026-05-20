from uuid import UUID

from shared.schemas.base_schema import BaseSchema

class LoginResponse(BaseSchema):
    access_token: str
    toke_type: str
    used_id: UUID
    company_id: UUID
    full_name: str
    email: str