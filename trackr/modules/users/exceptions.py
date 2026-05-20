from core.exceptions.base import ConflictError


class EmailAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")
