from uuid import UUID

from shared.schemas import BaseSchema


class LoginResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    full_name: str
    company_id: UUID
    