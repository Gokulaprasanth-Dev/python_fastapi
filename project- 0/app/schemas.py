from pydantic import BaseModel, Field


class ProductCreate(BaseModel):

    name: str = Field(..., min_length=1)

    price: float = Field(..., gt=0)

    category: str


class LoginRequest(BaseModel):

    username: str

    password: str
