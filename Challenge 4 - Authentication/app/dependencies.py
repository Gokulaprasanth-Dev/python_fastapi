from functools import lru_cache

from app.core.database import database
from app.repository.user_repository import UserRepository
from app.services.auth_service import AuthService


@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository(db=database)


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(user_repository=get_user_repository())
