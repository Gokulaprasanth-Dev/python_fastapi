from modules.users.protocols import UserReader

from modules.auth.schemas.login_request_schema import LoginRequest
from modules.auth.schemas.login_response_schema import LoginResponse

from modules.auth.exceptions import InvalidCredentialsError, InactiveAccountError

from core.security.password import verify_password
from core.security.jwt import create_access_token


class LoginService:
    def __init__(self, user_reader: UserReader) -> None:
        self.user_reader = user_reader

    async def execute(self, data: LoginRequest) -> LoginResponse:

        user = await self.user_reader.get_user_by_email(data.email)

        if not user:
            raise InvalidCredentialsError()

        is_password_valid = verify_password(
            data.password,
            user["hashed_password"],
        )

        if not is_password_valid:
            raise InvalidCredentialsError()

        if not user.get("is_active", True):
            raise InactiveAccountError()  # FIX #3: was missing ()

        access_token = create_access_token(
            data={
                "sub": user["id"],
                "email": user["email"],
                "role": user["role"],
            }
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user["id"],
            company_id=user["company_id"],
            full_name=user["full_name"],
            email=user["email"],
        )