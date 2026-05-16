from fastapi import Depends, APIRouter

from app.dependencies import get_auth_service
from app.middleware.auth_middleware import get_current_user
from app.schemas.auth_schema import LoginRequestSchema, TokenResponseSchema, LogoutResponseSchema
from app.services.auth_service import AuthService



router =APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login",response_model=TokenResponseSchema)
async def login(
    payload: LoginRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(email=payload.email,password=payload.password)    

# @router.post("/logout",LogoutResponseSchema)
# async def logout(current_user=Depends(get_current_user)):
#     return {
#         "message": "Logout successful"
#     }
