"""
LoginService — verifies credentials and issues a JWT access token.

Depends only on:
  - UserReader protocol (no Motor, no FastAPI)
  - core/security/password.py for bcrypt verification
  - core/security/jwt.py for token creation

HTTPException never appears here.
"""

from modules.auth.exceptions import InvalidCredentialsError
from modules.auth.schemas.requests import LoginRequest
from modules.auth.schemas.responses import LoginResponse
from modules.users.protocols import UserReader
from core.security.jwt import create_access_token
from core.security.password import verify_password


class LoginService:
    def __init__(self, user_reader: UserReader) -> None:
        self._user_reader = user_reader

    async def execute(self, data: LoginRequest) -> LoginResponse:
        # 1. Look up user — same vague error whether email or password is wrong
        #    (prevents user-enumeration attacks)
        user = await self._user_reader.get_by_email(data.email)
        if user is None:
            raise InvalidCredentialsError()

        # 2. Verify password
        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError()

        # 3. Guard inactive accounts
        if not user.is_active:
            raise InvalidCredentialsError()

        # 4. Issue token
        token = create_access_token(user_id=user.id, email=user.email)

        return LoginResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            company_id=user.company_id,
        )
