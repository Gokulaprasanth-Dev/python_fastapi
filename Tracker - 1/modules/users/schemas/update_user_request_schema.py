from pydantic import Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from shared.schemas.base_schema import BaseSchema

_ALLOWED_GENDERS = {"male", "female", "non-binary", "prefer_not_to_say", "other"}


class UpdateUserRequest(BaseSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: PhoneNumber | None = None
    gender: str | None = Field(default=None, max_length=40)
    desc: str | None = Field(default=None, max_length=500)

    # profile_image_url is intentionally excluded here.
    # It is only writable via POST /{user_id}/avatar which enforces
    # file-type validation, size limits, and S3 storage.

    @field_validator("full_name", "desc", mode="before")
    @classmethod
    def strip_html(cls, v: str | None) -> str | None:
        """
        Strip angle-bracket tags from free-text fields so client-rendered
        content can never contain injected HTML or script fragments.
        """
        if v is None:
            return v
        import re
        return re.sub(r"<[^>]*>", "", v).strip()

    @field_validator("gender", mode="before")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        if v is None:
            return v
        normalised = v.strip().lower()
        if normalised not in _ALLOWED_GENDERS:
            from core.exceptions.base import ValidationError
            raise ValidationError(
                "Invalid gender value",
                details={"allowed": sorted(_ALLOWED_GENDERS)},
            )
        return normalised
