from pydantic import BaseModel, EmailStr, Field

class ProfileResponeSchema(BaseModel):
    
    email : EmailStr
    
    name : str | None
    
    gender : str | None
    
    desc : str | None
    
    profile_image : str | None
    
    role : str 

class UpdateProfileSchema(BaseModel):
    
    name : str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    
    gender : str | None = Field(
        default=None,
        max_length=20
    )
    
    desc : str | None = Field(
        default=None,
        max_length=100
    )
    
class ProfileImageResponse(BaseModel):
    
    profile_image_url: str
    
    message : str

class ProfileUpdateResponseSchema(BaseModel):
    
    message: str        