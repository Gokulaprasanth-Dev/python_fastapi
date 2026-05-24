from typing import Any


class DomainError(Exception):
    """
    Base exception for all business/domain errors.
    """

    status_code: int = 400
    error_code: str = "DOMAIN_ERROR"

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}

        super().__init__(message)


class ValidationError(DomainError):
    status_code = 422
    error_code = "VALIDATION_ERROR"


class NotFoundError(DomainError):
    status_code = 404
    error_code = "NOT_FOUND"


class ConflictError(DomainError):
    status_code = 409
    error_code = "CONFLICT"


class UnauthorizedError(DomainError):
    status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenError(DomainError):
    status_code = 403
    error_code = "FORBIDDEN"