from pydantic_extra_types.phone_numbers import PhoneNumber
from shared.schemas.base_schema import BaseSchema


class UpdateUserRequest(BaseSchema):
    full_name: str | None = None
    phone: PhoneNumber | None = None
    gender: str | None = None
    desc: str | None = None
    # profile_image_url is intentionally excluded here.
    # It is only writable via POST /{user_id}/avatar which enforces
    # file-type validation, size limits, and S3 storage. Allowing it
    # as a free-form string here would let any client set an arbitrary URL.
