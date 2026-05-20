from shared.schemas.base_schema import BaseSchema

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

class RegisterRequest(BaseSchema):
    # Company fields
    company_name: str
    company_country: str
    company_industry: str
    
    # Admin user fields
    full_name: str
    email: EmailStr
    password: str = Field( min_length= 8)
    phone: PhoneNumber