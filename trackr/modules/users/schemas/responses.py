from uuid import UUID

from shared.schemas import BaseSchema


class RegisterResponse(BaseSchema):
    user_id: UUID
    company_id: UUID
    email: str
    full_name: str
    company_name: str

    # hashed_password is NEVER included here — not now, not ever
