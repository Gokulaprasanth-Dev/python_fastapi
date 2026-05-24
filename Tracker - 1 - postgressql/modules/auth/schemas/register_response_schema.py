from uuid import UUID

from shared.schemas.base_schema import BaseSchema


class RegisterResponse(BaseSchema):
    user_id: UUID
    company_id: UUID
    email: str
    full_name: str
    company_name: str