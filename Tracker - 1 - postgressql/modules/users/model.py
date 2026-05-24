from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field

from uuid import UUID, uuid4

from shared.schemas.base_schema import BaseSchema

class UserModel(BaseSchema):
    
    id : UUID = Field(
        default_factory=uuid4
    )
    company_id: UUID
    
    email : EmailStr 
    
    hashed_password : str
    
    full_name : str | None = None
    
    phone : str | None = None
    
    gender : str | None = None
    
    desc : str | None = None
    
    profile_image_url : str | None = None
    
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