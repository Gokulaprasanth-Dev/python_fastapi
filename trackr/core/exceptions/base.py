class DomainError(Exception):
    """Base for all domain-level errors."""


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist."""


class ConflictError(DomainError):
    """Raised when an operation conflicts with existing state."""


class ValidationError(DomainError):
    """Raised when input fails domain-level validation rules."""
