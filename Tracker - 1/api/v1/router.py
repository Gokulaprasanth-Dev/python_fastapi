from fastapi import APIRouter

from modules.auth.router import router as auth_router
from modules.users.router import router as users_router

v1_router = APIRouter()
v1_router.include_router(auth_router)
v1_router.include_router(users_router)