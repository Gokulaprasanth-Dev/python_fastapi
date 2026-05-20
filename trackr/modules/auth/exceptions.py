from core.exceptions.base import DomainError


class InvalidCredentialsError(DomainError):
    """Raised when email is not found or password does not match."""

    def __init__(self) -> None:
        # Deliberately vague -- do not reveal which field was wrong
        super().__init__("Invalid email or password")


class TokenExpiredError(DomainError):
    """Raised when a JWT access token has expired."""

    def __init__(self) -> None:
        super().__init__("Token has expired")


class InvalidTokenError(DomainError):
    """Raised when a JWT token is malformed or signature is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid token")


class TokenRevokedError(DomainError):
    """Raised when a valid token has been explicitly revoked (logged out)."""

    def __init__(self) -> None:
        super().__init__("Token has been revoked")
