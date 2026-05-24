from uuid import UUID
from shared.schemas.base_schema import BaseSchema


class UpdateUserResponse(BaseSchema):
    user_id: UUID
    full_name: str | None
    phone: str | None
    gender: str | None
    desc: str | None
    profile_image_url: str | None