import re

from pydantic import EmailStr, field_validator

from shared.enums import CompanyIndustry
from shared.schemas import BaseSchema

# E.164: + followed by 7–15 digits
_E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")


class RegisterRequest(BaseSchema):
    # Company fields
    company_name: str
    company_country: str
    company_industry: CompanyIndustry  # enum — validated and consistent

    # Admin user fields
    full_name: str
    email: EmailStr
    password: str
    phone: str  # must be E.164 format, e.g. +919876543210

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("phone")
    @classmethod
    def phone_e164(cls, v: str) -> str:
        if not _E164_RE.match(v):
            raise ValueError(
                "Phone must be in E.164 format (e.g. +919876543210)"
            )
        return v
