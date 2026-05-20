from shared.schemas.base_schema import BaseSchema
from pydantic import EmailStr,Field 

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(
        min_length=8
    ) 