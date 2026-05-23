from pydantic import Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from shared.schemas.base_schema import BaseSchema


class UpdateUserRequest(BaseSchema):
    full_name: str | None = None
    phone: PhoneNumber | None = None
    gender: str | None = None
    desc: str | None = None
    profile_image_url: str | None = None