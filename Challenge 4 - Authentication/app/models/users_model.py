from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field

class UserModel(BaseModel):
    
    email : EmailStr
    
    hashed_password : str
    
    name : str | None = None
    
    gender : str | None = None
    
    desc : str | None = None
    
    profile_image : str | None = None
    
    role : str = "user"
    
    is_active : bool = True
    
    is_verified : bool = False
    
    created_at : datetime = Field(
        default_factory= lambda: datetime.now(timezone.utc)
    )
    
    updated_at : datetime = Field(
        default_factory= lambda: datetime.now(timezone.utc)
    )
    
    last_login : datetime | None = None    