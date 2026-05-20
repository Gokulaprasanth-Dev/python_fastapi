from core.exceptions.base import UnauthorizedError
        
from core.exceptions.base import ConflictError

from core.exceptions.base import ForbiddenError

class InvalidCredentialsError(UnauthorizedError):
    error_code = "INVALID_CREDENTIALS"

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InvalidTokenError(UnauthorizedError):
    error_code = "INVALID_TOKEN"

    def __init__(self) -> None:
        super().__init__("Invalid authentication token")


class TokenExpiredError(UnauthorizedError):
    error_code = "TOKEN_EXPIRED"

    def __init__(self) -> None:
        super().__init__("Authentication token expired")


class TokenRevokedError(UnauthorizedError):
    error_code = "TOKEN_REVOKED"

    def __init__(self) -> None:
        super().__init__("Authentication token revoked")
        



class EmailAlreadyExistsError(ConflictError):
    error_code = "EMAIL_ALREADY_EXISTS"

    def __init__(self, email: str) -> None:
        super().__init__(
            message="Email already registered",
            details={"email": email},
        )



class InactiveAccountError(ForbiddenError):
    error_code = "ACCOUNT_INACTIVE"

    def __init__(self) -> None:
        super().__init__("Account is inactive")        