from pydantic import EmailStr

from shared.schemas import BaseSchema


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str
