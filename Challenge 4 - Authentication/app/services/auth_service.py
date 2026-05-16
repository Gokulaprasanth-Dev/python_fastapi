from fastapi import HTTPException, status

from app.core.security import create_access_token
from app.repository.user_repository import UserRepository
from app.utils.password import verify_password

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    async def login(self,email:str,password:str):
        
        user= await self.user_repository.get_user_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail= "Invaild email or password"
            )
        
        is_password_vaild=verify_password(
            password,
            user["hashed_password"]
        )
        
        if not is_password_vaild:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail= "Invaild email or password"
            )
        
        if not user.get("is_active",True):
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail= "Account is inactive"
            )
        
        access_token =create_access_token(
            data={
                "sub": str(user["_id"]),
                "email": user["email"],
                "role": user["role"]        
                }
        )
        
        await self.user_repository.update_last_login(
            str(user["_id"])
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }