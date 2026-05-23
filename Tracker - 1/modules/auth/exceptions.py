from core.exceptions.base import UnauthorizedError, ForbiddenError

# EmailAlreadyExistsError lives in modules.users.exceptions — the canonical owner
# of email/user domain errors. Import it here for backwards compatibility so
# any existing code that does `from modules.auth.exceptions import EmailAlreadyExistsError`
# continues to work without change.
from modules.users.exceptions import EmailAlreadyExistsError  # noqa: F401


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


class InactiveAccountError(ForbiddenError):
    error_code = "ACCOUNT_INACTIVE"

    def __init__(self) -> None:
        super().__init__("Account is inactive")
